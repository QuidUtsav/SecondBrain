# routers/query.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth.security import get_current_account
from schemas.query import QueryRequest, QueryResponse, SourceEntry
from services.intent_extraction import extract_intent
from services.embedding import get_embedding
from services.hybrid_search import hybrid_search, date_only_fetch
from services.rag_response import generate_answer

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/", response_model=QueryResponse)
def query_entries(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_account=Depends(get_current_account),
):
    intent = extract_intent(request.query)

    start_date = intent.get("start_date")
    end_date = intent.get("end_date")
    topic = intent.get("topic")

    if intent["intent"] == "date_only":
        entries = date_only_fetch(
            db,
            account_id=current_account.id,
            start_date=start_date,
            end_date=end_date,
        )
    else:
        query_embedding = get_embedding(request.query if not topic else topic)
        entries = hybrid_search(
            db,
            account_id=current_account.id,
            query=topic or request.query,
            query_embedding=query_embedding,
            start_date=start_date,
            end_date=end_date,
        )

    answer = generate_answer(request.query, entries)

    return QueryResponse(
        answer=answer,
        sources=[
            SourceEntry(id=e.id, raw_text=e.raw_text, entry_date=e.entry_date)
            for e in entries
        ],
    )
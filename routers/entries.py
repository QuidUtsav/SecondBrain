# routers/entries.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import get_db
from models.entry import Entry
from schemas.entry import EntryCreate, EntryResponse
from services.embedding import get_embedding
from auth.security import get_current_account

router = APIRouter(prefix="/entries", tags=["entries"])


@router.post("/", response_model=EntryResponse)
def create_entry(
    entry: EntryCreate,
    db: Session = Depends(get_db),
    current_account=Depends(get_current_account),
):
    embedding = get_embedding(entry.raw_text)

    new_entry = Entry(
        account_id=current_account.id,
        raw_text=entry.raw_text,
        embedding=embedding,
    )
    if entry.entry_date is not None:
        new_entry.entry_date = entry.entry_date

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry


@router.get("/", response_model=list[EntryResponse])
def list_entries(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_account=Depends(get_current_account),
):
    offset = (page - 1) * page_size
    stmt = (
        select(Entry)
        .where(Entry.account_id == current_account.id)
        .order_by(Entry.entry_date.desc())
        .offset(offset)
        .limit(page_size)
    )
    return db.execute(stmt).scalars().all()
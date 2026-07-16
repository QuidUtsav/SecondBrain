# services/hybrid_search.py

import numpy as np
from rank_bm25 import BM25Okapi
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.entry import Entry

STOP_WORDS = {"is", "in", "the", "a", "an", "of", "and", "to", "it", "what", "how", "why"}


def tokenize(text: str) -> list[str]:
    return [w.lower() for w in text.split() if w.lower() not in STOP_WORDS]


def fetch_candidates(
    db: Session,
    account_id: int,
    start_date=None,
    end_date=None,
) -> list[Entry]:
    """
    SQL-filtered candidate set. account_id is always required.
    Date filters are applied only when provided (topic_only queries skip them).
    """
    stmt = select(Entry).where(Entry.account_id == account_id)

    if start_date is not None:
        stmt = stmt.where(Entry.entry_date >= start_date)
    if end_date is not None:
        stmt = stmt.where(Entry.entry_date <= end_date)

    return db.execute(stmt).scalars().all()


def vector_rank(
    db: Session,
    account_id: int,
    query_embedding: list[float],
    start_date=None,
    end_date=None,
    top_k: int = 10,
) -> list[Entry]:
    """
    pgvector native similarity search, scoped to the same SQL filters.
    Uses cosine distance operator (<=>) rather than L2, matching MiniLM's
    intended similarity space.
    """
    stmt = select(Entry).where(Entry.account_id == account_id)

    if start_date is not None:
        stmt = stmt.where(Entry.entry_date >= start_date)
    if end_date is not None:
        stmt = stmt.where(Entry.entry_date <= end_date)

    stmt = stmt.order_by(Entry.embedding.cosine_distance(query_embedding)).limit(top_k)

    return db.execute(stmt).scalars().all()


def bm25_rank(query: str, candidates: list[Entry], top_k: int = 10) -> list[Entry]:
    if not candidates:
        return []

    tokenized_corpus = [tokenize(entry.raw_text) for entry in candidates]
    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)

    ranked_indices = np.argsort(scores)[-top_k:][::-1]
    return [candidates[i] for i in ranked_indices]


def hybrid_search(
    db: Session,
    account_id: int,
    query: str,
    query_embedding: list[float],
    start_date=None,
    end_date=None,
    top_k: int = 3,
    k: int = 60,
) -> list[Entry]:
    """
    RRF fusion of pgvector cosine-similarity ranking and BM25 ranking,
    both scoped to the same account_id + date filters.
    """
    candidates = fetch_candidates(db, account_id, start_date, end_date)
    if not candidates:
        return []

    vector_results = vector_rank(db, account_id, query_embedding, start_date, end_date, top_k=len(candidates))
    vector_rank_map = {entry.id: rank for rank, entry in enumerate(vector_results)}

    bm25_results = bm25_rank(query, candidates, top_k=len(candidates))
    bm25_rank_map = {entry.id: rank for rank, entry in enumerate(bm25_results)}

    scored = []
    for entry in candidates:
        v_rank = vector_rank_map.get(entry.id, len(candidates))
        b_rank = bm25_rank_map.get(entry.id, len(candidates))
        rrf_score = 1 / (k + v_rank) + 1 / (k + b_rank)
        scored.append((rrf_score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:top_k]]


def date_only_fetch(
    db: Session,
    account_id: int,
    start_date=None,
    end_date=None,
) -> list[Entry]:
    """
    For date_only intent — no ranking, just chronological listing
    within the SQL-filtered date range.
    """
    stmt = (
        select(Entry)
        .where(Entry.account_id == account_id)
        .order_by(Entry.entry_date.asc())
    )

    if start_date is not None:
        stmt = stmt.where(Entry.entry_date >= start_date)
    if end_date is not None:
        stmt = stmt.where(Entry.entry_date <= end_date)

    return db.execute(stmt).scalars().all()
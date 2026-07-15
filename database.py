from pydantic import BaseModel
from datetime import date, datetime

# schemas/entry.py

class EntryCreate(BaseModel):
    raw_text: str
    entry_date: date | None = None  # optional override, server defaults if absent

class EntryResponse(BaseModel):
    id: int
    raw_text: str
    entry_date: date
    created_at: datetime

    class Config:
        from_attributes = True


# schemas/query.py

class QueryRequest(BaseModel):
    query: str

class SourceEntry(BaseModel):
    id: int
    raw_text: str
    entry_date: date

class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceEntry]
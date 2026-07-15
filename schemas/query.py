from pydantic import BaseModel
from datetime import date, datetime


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
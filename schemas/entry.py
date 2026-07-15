# schemas/entry.py
from pydantic import BaseModel
from datetime import date, datetime

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

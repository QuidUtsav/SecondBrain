# models/entry.py

from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, ForeignKey, Text
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from database import Base


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    raw_text = Column(Text, nullable=False)
    entry_date = Column(Date, nullable=False, server_default=func.current_date(), index=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    embedding = Column(Vector(384), nullable=False)
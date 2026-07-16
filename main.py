# main.py

from fastapi import FastAPI
from database import engine, Base
from routers import entries, query, auth

app = FastAPI(title="Second Brain")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(entries.router)
app.include_router(query.router)


@app.get("/")
def root():
    return {"status": "Second Brain is running"}
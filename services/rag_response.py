# services/rag_response.py

import os
from groq import Groq
from models.entry import Entry

client = Groq(api_key=os.getenv("AI_API_KEY"))

SYSTEM_PROMPT = """You are a personal journal assistant. Answer the user's question
using ONLY the journal entries provided as context below. Each entry has a date and text.

Rules:
- Only use information present in the provided entries. Do not invent or assume anything not stated.
- If multiple entries are relevant, synthesize them into one coherent answer, referencing dates where it helps clarity.
- If the provided entries are empty or clearly don't answer the question, say so plainly instead of guessing.
- Keep the answer conversational and concise, like a helpful assistant recalling notes.

Journal entries:
{context}
"""


def format_context(entries: list[Entry]) -> str:
    if not entries:
        return "(no entries found)"
    return "\n".join(f"- [{entry.entry_date}] {entry.raw_text}" for entry in entries)


def generate_answer(user_query: str, entries: list[Entry]) -> str:
    context = format_context(entries)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
            {"role": "user", "content": user_query},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content
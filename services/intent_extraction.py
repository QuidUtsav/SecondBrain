# services/intent_extraction.py

import os
import json
from datetime import date
from groq import Groq

client = Groq(api_key=os.getenv("AI_API_KEY"))

SYSTEM_PROMPT = """You are a query intent extractor for a personal journal app.
Given a user's question and today's date, extract structured intent as JSON only — no other text.

Return exactly this shape:
{{
  "intent": "date_only" | "topic_only" | "date_and_topic",
  "start_date": "YYYY-MM-DD" or null,
  "end_date": "YYYY-MM-DD" or null,
  "topic": "string" or null
}}

Rules:
- "date_only": user asks about a specific date/range with no topic (e.g. "what did I log on July 3rd").
- "topic_only": user asks about a subject with no date mentioned (e.g. "what did I say about my car insurance").
- "date_and_topic": both a date/range and a subject are present.
- Resolve relative dates (e.g. "last Tuesday", "three days ago") using today's date, which is {today}.
- If no date is mentioned, start_date and end_date must be null.
- If no topic is mentioned, topic must be null.
- Output ONLY the JSON object, nothing else.
"""


def extract_intent(user_query: str) -> dict:
    today = date.today().isoformat()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(today=today)},
            {"role": "user", "content": user_query},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    raw = response.choices[0].message.content
    return json.loads(raw)
import sys
sys.path.insert(0, '.')

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from app.database.supabase_client import get_supabase_admin
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.5,
        max_tokens=2048
    )

def generate_mcqs(context: str, topic: str, num_questions: int = 5) -> list:
    llm = get_llm()

    system_prompt = """You are an expert quiz maker. Generate MCQs strictly in JSON format.
Return ONLY a JSON array, no extra text, no markdown, no explanation.

Format:
[
  {
    "question": "Question text here?",
    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
    "correct": "A) option1",
    "explanation": "Brief explanation of why this is correct"
  }
]"""

    user_prompt = f"""Generate {num_questions} multiple choice questions about "{topic}" from this content:

{context}

Return ONLY the JSON array."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return []

def generate_flashcards(context: str, topic: str, num_cards: int = 8) -> list:
    llm = get_llm()

    system_prompt = """You are a flashcard creator. Generate flashcards strictly in JSON format.
Return ONLY a JSON array, no extra text.

Format:
[
  {
    "front": "Key term or concept",
    "back": "Clear definition or explanation"
  }
]"""

    user_prompt = f"""Generate {num_cards} flashcards for key concepts about "{topic}" from this content:

{context}

Return ONLY the JSON array."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return []

def save_quiz_attempt(user_id: str, document_id: str, topic: str, score: int, total: int):
    supabase = get_supabase_admin()
    supabase.table("quiz_attempts").insert({
        "user_id": user_id,
        "document_id": document_id,
        "topic": topic,
        "score": score,
        "total_questions": total
    }).execute()
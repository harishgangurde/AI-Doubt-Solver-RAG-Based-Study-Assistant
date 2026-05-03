import sys
sys.path.insert(0, '.')

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from app.database.vector_store import search_similar_chunks
from app.database.supabase_client import get_supabase_admin
from dotenv import load_dotenv
import os

load_dotenv()

def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.3,
        max_tokens=1024
    )

def answer_doubt(question: str, user_id: str, document_id: str, chat_history: list = []) -> str:
    
    # Handle conversational messages — don't do RAG for these
    conversational = ["okay", "thanks", "thank you", "ok", "got it", "sure", 
                      "alright", "cool", "nice", "great", "bye", "hello", "hi"]
    
    if question.lower().strip().rstrip("!.,") in conversational:
        return "You're welcome! 😊 Feel free to ask any more doubts from your document."

    chunks = search_similar_chunks(question, user_id, document_id, top_k=5)
    if not chunks:
        return "I couldn't find relevant information in your document. Try rephrasing your question."

    context = "\n\n".join([chunk["content"] for chunk in chunks])

    system_prompt = f"""You are a helpful AI tutor. Answer the student's LATEST question only.

    Context from the document:
    {context}

    Rules:
    - Answer ONLY the latest question asked
    - Do NOT repeat or re-answer previous questions from history
    - Answer clearly and in simple language
    - If not in context, say "This topic is not covered in the uploaded document"
    - Use bullet points when explaining concepts
    - Keep answers concise but complete
    """

    messages = [SystemMessage(content=system_prompt)]

    # Only send last 4 exchanges for memory, not entire history
    for msg in chat_history[-6:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=question))

    llm = get_llm()
    response = llm.invoke(messages)
    return response.content

def save_chat_message(session_id: str, role: str, content: str):
    supabase = get_supabase_admin()
    supabase.table("chat_messages").insert({
        "session_id": session_id,
        "role": role,
        "content": content
    }).execute()

def get_chat_history(session_id: str) -> list:
    supabase = get_supabase_admin()
    response = supabase.table("chat_messages")\
        .select("role, content")\
        .eq("session_id", session_id)\
        .order("created_at")\
        .execute()
    return response.data

def create_chat_session(user_id: str, document_id: str, title: str) -> str:
    supabase = get_supabase_admin()
    response = supabase.table("chat_sessions").insert({
        "user_id": user_id,
        "document_id": document_id,
        "title": title
    }).execute()
    return response.data[0]["id"]
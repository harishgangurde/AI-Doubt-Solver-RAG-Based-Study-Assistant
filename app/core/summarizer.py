from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
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

def summarize_topic(context: str, topic: str) -> str:
    """Generate a crisp summary of a topic from document context."""
    llm = get_llm()

    system_prompt = """You are a study assistant. Create clear, concise summaries for students.
Format your response as:
- 3-5 bullet points covering the main ideas
- Each point should be one clear sentence
- End with one "Key takeaway" line"""

    user_prompt = f"""Summarize the topic "{topic}" based on this content:

{context}"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = llm.invoke(messages)
    return response.content
import sys
sys.path.insert(0, '.')

import fitz
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from app.database.supabase_client import get_supabase_admin
import streamlit as st

@st.cache_resource(show_spinner="Loading AI model...")
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf(pdf_file) -> str:
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text

def chunk_text(text: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    return splitter.split_text(text)

def embed_chunks(chunks: list) -> list:
    model = load_embedding_model()
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings.tolist()

def process_and_store_pdf(pdf_file, user_id: str, subject: str) -> dict:
    supabase = get_supabase_admin()

    text = extract_text_from_pdf(pdf_file)
    if not text.strip():
        raise ValueError("Could not extract text from PDF. It may be scanned/image-based.")

    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("No content found after chunking.")

    doc_response = supabase.table("documents").insert({
        "user_id": user_id,
        "file_name": pdf_file.name,
        "subject": subject,
        "total_chunks": len(chunks)
    }).execute()

    document_id = doc_response.data[0]["id"]
    embeddings = embed_chunks(chunks)

    chunk_records = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_records.append({
            "document_id": document_id,
            "user_id": user_id,
            "content": chunk,
            "embedding": embedding,
            "chunk_index": i
        })

    batch_size = 50
    for i in range(0, len(chunk_records), batch_size):
        batch = chunk_records[i:i + batch_size]
        supabase.table("document_chunks").insert(batch).execute()

    return {
        "document_id": document_id,
        "file_name": pdf_file.name,
        "total_chunks": len(chunks)
    }

def get_user_documents(user_id: str) -> list:
    supabase = get_supabase_admin()
    response = supabase.table("documents")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .execute()
    return response.data

def delete_document(document_id: str, user_id: str):
    supabase = get_supabase_admin()
    supabase.table("documents")\
        .delete()\
        .eq("id", document_id)\
        .eq("user_id", user_id)\
        .execute()
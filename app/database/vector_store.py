import sys
sys.path.insert(0, '.')

from sentence_transformers import SentenceTransformer
from app.database.supabase_client import get_supabase_admin
import streamlit as st

@st.cache_resource(show_spinner="Loading AI model...")
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def search_similar_chunks(query: str, user_id: str, document_id: str, top_k: int = 5) -> list:
    model = load_embedding_model()
    query_embedding = model.encode(query).tolist()

    supabase = get_supabase_admin()
    response = supabase.rpc("match_chunks", {
        "query_embedding": query_embedding,
        "match_user_id": user_id,
        "match_document_id": document_id,
        "match_count": top_k
    }).execute()

    return response.data
import streamlit as st
from app.database.vector_store import search_similar_chunks

@st.cache_data
def cached_search(query, user_id, doc_id):
    return search_similar_chunks(query, user_id, doc_id)
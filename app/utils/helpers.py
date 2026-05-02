import streamlit as st

def init_session_state():
    """Initialize all Streamlit session state variables."""
    defaults = {
        "user": None,
        "user_id": None,
        "selected_document": None,
        "selected_document_id": None,
        "chat_session_id": None,
        "chat_history": [],
        "quiz_questions": [],
        "flashcards": [],
        "current_card_index": 0,
        "card_flipped": False,
        "quiz_score": 0,
        "quiz_submitted": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def is_logged_in() -> bool:
    return st.session_state.get("user_id") is not None

def require_login():
    """Show login warning if not authenticated."""
    if not is_logged_in():
        st.warning("Please login first from the Home page.")
        st.stop()

def require_document():
    """Show warning if no document is selected."""
    if not st.session_state.get("selected_document_id"):
        st.info("Please upload or select a document from the Home page first.")
        st.stop()
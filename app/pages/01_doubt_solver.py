import streamlit as st  # ✅ MUST BE FIRST

st.set_page_config(page_title="Doubt Solver", page_icon="💬", layout="wide")

import sys
sys.path.insert(0, '.')

from app.utils.helpers import init_session_state, require_login, require_document
from app.components.sidebar import show_sidebar

# NEW IMPORTS
from app.core.rag_pipeline import get_context
from app.core.tutor_modes import modify_prompt
from app.components.sources_viewer import show_sources

# ================= INIT =================
init_session_state()
require_login()
show_sidebar()

st.title("💬 Doubt Solver")
st.markdown("Ask anything from your uploaded document.")

require_document()

# ================= SESSION =================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_chunks" not in st.session_state:
    st.session_state.last_chunks = []

# ================= MODE =================
mode = st.selectbox("🎓 Select Mode", ["Beginner", "Intermediate", "Interview"])

# ================= CHAT =================
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ================= INPUT =================
if prompt := st.chat_input("Ask your doubt here..."):

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.chat_history.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            chunks, context = get_context(
                prompt,
                st.session_state.user_id,
                st.session_state.selected_document_id
            )

            answer = f"Based on your document:\n\n{context[:800]}"
            answer = modify_prompt(answer, mode)

            st.markdown(answer)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer
    })

    st.session_state.last_chunks = chunks

# ================= SOURCES =================
if st.session_state.last_chunks:
    show_sources(st.session_state.last_chunks)

# ================= CLEAR =================
if st.session_state.chat_history:
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.last_chunks = []
        st.rerun()
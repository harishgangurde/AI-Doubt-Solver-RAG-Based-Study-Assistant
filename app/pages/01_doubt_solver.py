import streamlit as st
st.set_page_config(page_title="Doubt Solver", page_icon="💬", layout="wide")

import sys
sys.path.insert(0, '.')

from app.utils.helpers import init_session_state, require_login, require_document
from app.components.sidebar import show_sidebar
from app.core.rag_chain import answer_doubt, save_chat_message, get_chat_history, create_chat_session

init_session_state()
require_login()
show_sidebar()

st.title("💬 Doubt Solver")
st.markdown("Ask anything from your uploaded document.")

require_document()

# Mode selector — only once, right here
mode = st.selectbox(
    "🎓 Select Mode",
    ["Beginner", "Intermediate", "Expert"],
    help="Beginner = simple language, Expert = technical depth"
)

mode_prompts = {
    "Beginner": "Explain in very simple language as if to a school student. Avoid jargon.",
    "Intermediate": "Explain clearly with some technical terms. Assume basic knowledge.",
    "Expert": "Explain in full technical depth with precise terminology."
}

# Create chat session if not exists
if not st.session_state.chat_session_id:
    session_id = create_chat_session(
        st.session_state.user_id,
        st.session_state.selected_document_id,
        f"Session - {st.session_state.selected_document}"
    )
    st.session_state.chat_session_id = session_id
    st.session_state.chat_history = []

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask your doubt here..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.chat_history.append({"role": "user", "content": prompt})
    save_chat_message(st.session_state.chat_session_id, "user", prompt)

    # Inject mode into question
    mode_instruction = mode_prompts[mode]
    enhanced_prompt = f"{prompt}\n\n[Answer style: {mode_instruction}]"

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = answer_doubt(
                question=enhanced_prompt,
                user_id=st.session_state.user_id,
                document_id=st.session_state.selected_document_id,
                chat_history=st.session_state.chat_history
            )
            st.markdown(answer)

    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    save_chat_message(st.session_state.chat_session_id, "assistant", answer)

if st.session_state.chat_history:
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.chat_session_id = None
        st.rerun()
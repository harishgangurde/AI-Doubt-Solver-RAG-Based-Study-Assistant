import sys
sys.path.insert(0, '.')

import streamlit as st
from app.utils.helpers import init_session_state, require_login, require_document
from app.components.sidebar import show_sidebar
from app.core.quiz_generator import generate_flashcards
from app.database.vector_store import search_similar_chunks

st.set_page_config(page_title="Flashcards", page_icon="🃏", layout="wide")

init_session_state()
require_login()
show_sidebar()

st.title("🃏 Flashcards")
st.markdown("Review key concepts with AI-generated flashcards.")

require_document()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ Settings")
    topic = st.text_input("Topic for flashcards", placeholder="e.g. Sorting Algorithms...")
    num_cards = st.slider("Number of cards", min_value=4, max_value=15, value=8)

    if st.button("Generate Flashcards", type="primary", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Creating flashcards..."):
                chunks = search_similar_chunks(
                    topic,
                    st.session_state.user_id,
                    st.session_state.selected_document_id,
                    top_k=6
                )
                if not chunks:
                    st.error("No relevant content found for this topic.")
                else:
                    context = "\n\n".join([c["content"] for c in chunks])
                    cards = generate_flashcards(context, topic, num_cards)
                    if cards:
                        st.session_state.flashcards = cards
                        st.session_state.current_card_index = 0
                        st.session_state.card_flipped = False
                        st.rerun()
                    else:
                        st.error("Could not generate flashcards. Try a different topic.")

with col2:
    if st.session_state.get("flashcards"):
        cards = st.session_state.flashcards
        idx = st.session_state.current_card_index
        flipped = st.session_state.card_flipped
        total = len(cards)

        st.subheader(f"Card {idx + 1} of {total}")
        st.progress((idx + 1) / total)

        card = cards[idx]

        # Card display
        if not flipped:
            st.info(f"### 🔵 {card['front']}")
            st.caption("Click 'Flip' to see the answer")
        else:
            st.success(f"### 🟢 {card['back']}")
            st.caption("Click 'Next' for the next card")

        # Controls
        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.current_card_index = max(0, idx - 1)
                st.session_state.card_flipped = False
                st.rerun()

        with c2:
            if st.button("🔄 Flip", use_container_width=True, type="primary"):
                st.session_state.card_flipped = not flipped
                st.rerun()

        with c3:
            if st.button("➡️ Next", use_container_width=True):
                if idx + 1 < total:
                    st.session_state.current_card_index = idx + 1
                    st.session_state.card_flipped = False
                    st.rerun()
                else:
                    st.success("🎉 You've reviewed all cards!")

        st.markdown("---")

        # All cards overview
        with st.expander("📋 View all cards"):
            for i, c in enumerate(cards):
                st.markdown(f"**{i+1}. {c['front']}**")
                st.markdown(f"→ {c['back']}")
                st.markdown("")
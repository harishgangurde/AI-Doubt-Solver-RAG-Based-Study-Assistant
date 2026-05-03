import streamlit as st
st.set_page_config(page_title="Flashcards", page_icon="🃏", layout="wide")

import sys
sys.path.insert(0, '.')

from app.utils.helpers import init_session_state, require_login, require_document
from app.components.sidebar import show_sidebar
from app.core.quiz_generator import generate_flashcards
from app.database.vector_store import search_similar_chunks

init_session_state()
require_login()
show_sidebar()

st.markdown("""
<style>
.flashcard-front {
    background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
    border: 2px solid #7c6aff;
    border-radius: 20px;
    padding: 50px 40px;
    text-align: center;
    min-height: 220px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 32px rgba(124, 106, 255, 0.3);
    margin: 10px 0;
}
.flashcard-back {
    background: linear-gradient(135deg, #0d2818, #1a3a2a);
    border: 2px solid #6affb8;
    border-radius: 20px;
    padding: 50px 40px;
    text-align: center;
    min-height: 220px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 32px rgba(106, 255, 184, 0.3);
    margin: 10px 0;
}
.card-label {
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 16px;
    font-weight: 600;
}
.card-term {
    font-size: 28px;
    font-weight: 700;
    color: #e8e8f0;
    line-height: 1.3;
}
.card-def {
    font-size: 18px;
    color: #c8f0dc;
    line-height: 1.6;
}
.card-hint {
    font-size: 12px;
    color: #555570;
    margin-top: 20px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.progress-text {
    font-size: 13px;
    color: #8888aa;
    text-align: center;
    margin-bottom: 8px;
}
.card-counter {
    font-size: 22px;
    font-weight: 800;
    color: #e8e8f0;
    text-align: center;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

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
        card = cards[idx]

        # Progress bar
        progress = (idx + 1) / total
        st.markdown(f'<div class="card-counter">Card {idx+1} of {total}</div>', unsafe_allow_html=True)
        st.progress(progress)

        # Card display
        if not flipped:
            st.markdown(f"""
            <div class="flashcard-front">
                <div class="card-label" style="color:#7c6aff;">📘 TERM</div>
                <div class="card-term">{card['front']}</div>
                <div class="card-hint">Click Flip to see the answer ↓</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="flashcard-back">
                <div class="card-label" style="color:#6affb8;">✅ ANSWER</div>
                <div class="card-def">{card['back']}</div>
                <div class="card-hint">Click Next for the next card →</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # Controls
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⬅️ Previous", use_container_width=True, disabled=(idx == 0)):
                st.session_state.current_card_index = max(0, idx - 1)
                st.session_state.card_flipped = False
                st.rerun()
        with c2:
            if st.button("🔄 Flip", use_container_width=True, type="primary"):
                st.session_state.card_flipped = not flipped
                st.rerun()
        with c3:
            if idx + 1 < total:
                if st.button("Next ➡️", use_container_width=True):
                    st.session_state.current_card_index = idx + 1
                    st.session_state.card_flipped = False
                    st.rerun()
            else:
                if st.button("🎉 Restart", use_container_width=True):
                    st.session_state.current_card_index = 0
                    st.session_state.card_flipped = False
                    st.rerun()

        st.markdown("---")

        # All cards overview
        with st.expander("📋 View all cards"):
            for i, c in enumerate(cards):
                active = "🟣" if i == idx else "⚪"
                st.markdown(f"**{active} {i+1}. {c['front']}**")
                st.markdown(f"→ {c['back']}")
                if st.button(f"Jump to card {i+1}", key=f"jump_{i}"):
                    st.session_state.current_card_index = i
                    st.session_state.card_flipped = False
                    st.rerun()
                st.markdown("---")
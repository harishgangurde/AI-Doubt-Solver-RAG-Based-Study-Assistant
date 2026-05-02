import streamlit as st  # ✅ MUST BE FIRST

st.set_page_config(page_title="Quiz Generator", page_icon="📝", layout="wide")

import sys
sys.path.insert(0, '.')

from app.utils.helpers import init_session_state, require_login, require_document
from app.components.sidebar import show_sidebar
from app.core.quiz_generator import generate_mcqs, save_quiz_attempt
from app.core.rag_pipeline import get_context

# ================= INIT =================
init_session_state()
require_login()
show_sidebar()

st.title("📝 Quiz Generator")
st.markdown("Test your knowledge with AI-generated MCQs.")

require_document()

# ================= ADAPTIVE =================
def adjust_difficulty(score, total):
    pct = (score / total) * 100
    if pct < 40:
        return "easy"
    elif pct < 70:
        return "medium"
    else:
        return "hard"

col1, col2 = st.columns([1, 2])

# ================= LEFT =================
with col1:
    st.subheader("⚙️ Settings")
    topic = st.text_input("Topic to quiz on")
    num_q = st.slider("Number of questions", 3, 10, 5)

    if st.button("Generate Quiz", type="primary", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Generating questions..."):

                chunks, context = get_context(
                    topic,
                    st.session_state.user_id,
                    st.session_state.selected_document_id
                )

                if not context:
                    st.error("No relevant content found.")
                else:
                    questions = generate_mcqs(context, topic, num_q)

                    if questions:
                        st.session_state.quiz_questions = questions
                        st.session_state.quiz_topic = topic
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_score = 0
                        st.session_state.user_answers = {}
                        st.session_state.quiz_context = context
                        st.rerun()

# ================= RIGHT =================
with col2:
    if st.session_state.get("quiz_questions"):
        questions = st.session_state.quiz_questions

        if not st.session_state.quiz_submitted:
            st.subheader(f"📋 {st.session_state.quiz_topic}")

            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}. {q['question']}**")

                ans = st.radio(
                    f"q{i}",
                    q["options"],
                    key=f"q_{i}",
                    index=None,
                    label_visibility="collapsed"
                )

                st.session_state.user_answers[i] = ans

            if st.button("Submit Quiz", type="primary", use_container_width=True):

                unanswered = [
                    i for i in range(len(questions))
                    if not st.session_state.user_answers.get(i)
                ]

                if unanswered:
                    st.warning(f"{len(unanswered)} unanswered")
                else:
                    score = sum(
                        1 for i, q in enumerate(questions)
                        if st.session_state.user_answers.get(i) == q["correct"]
                    )

                    st.session_state.quiz_score = score
                    st.session_state.quiz_submitted = True

                    save_quiz_attempt(
                        st.session_state.user_id,
                        st.session_state.selected_document_id,
                        st.session_state.quiz_topic,
                        score,
                        len(questions)
                    )

                    st.rerun()

        else:
            score = st.session_state.quiz_score
            total = len(questions)
            pct = round((score / total) * 100)

            st.success(f"Score: {score}/{total} ({pct}%)")

            difficulty = adjust_difficulty(score, total)
            st.info(f"Next Difficulty: {difficulty}")

            st.markdown("---")

            for i, q in enumerate(questions):
                with st.expander(f"Q{i+1}"):
                    st.write("Your:", st.session_state.user_answers.get(i))
                    st.write("Correct:", q["correct"])
                    st.write(q["explanation"])

            if st.button("Try Again"):
                questions = generate_mcqs(
                    st.session_state.quiz_context,
                    st.session_state.quiz_topic + f" difficulty:{difficulty}",
                    len(questions)
                )

                st.session_state.quiz_questions = questions
                st.session_state.quiz_submitted = False
                st.session_state.user_answers = {}
                st.rerun()
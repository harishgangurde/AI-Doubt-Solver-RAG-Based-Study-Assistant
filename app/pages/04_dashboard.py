import sys
sys.path.insert(0, '.')

import streamlit as st
import pandas as pd
from app.utils.helpers import init_session_state, require_login
from app.components.sidebar import show_sidebar
from app.database.supabase_client import get_supabase_admin

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

init_session_state()
require_login()
show_sidebar()

st.title("📊 Your Learning Dashboard")
st.markdown("Track your quiz performance and study progress.")

supabase = get_supabase_admin()

# Fetch quiz attempts
attempts = supabase.table("quiz_attempts")\
    .select("*")\
    .eq("user_id", st.session_state.user_id)\
    .order("created_at", desc=True)\
    .execute().data

# Fetch documents
docs = supabase.table("documents")\
    .select("*")\
    .eq("user_id", st.session_state.user_id)\
    .execute().data

# Top stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📄 Documents", len(docs))

with col2:
    st.metric("📝 Quizzes Taken", len(attempts))

with col3:
    if attempts:
        avg = round(sum(a["score"] / a["total_questions"] * 100 for a in attempts) / len(attempts))
        st.metric("📈 Avg Score", f"{avg}%")
    else:
        st.metric("📈 Avg Score", "N/A")

with col4:
    if attempts:
        best = max(round(a["score"] / a["total_questions"] * 100) for a in attempts)
        st.metric("🏆 Best Score", f"{best}%")
    else:
        st.metric("🏆 Best Score", "N/A")

st.markdown("---")

if not attempts:
    st.info("No quiz attempts yet. Take a quiz to see your progress here!")
else:
    df = pd.DataFrame(attempts)
    df["score_pct"] = (df["score"] / df["total_questions"] * 100).round()
    df["date"] = pd.to_datetime(df["created_at"]).dt.strftime("%d %b %Y")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.subheader("📈 Score Trend")
        chart_data = df[["date", "score_pct"]].rename(
            columns={"date": "Date", "score_pct": "Score (%)"}
        )
        st.line_chart(chart_data.set_index("Date"))

    with col_b:
        st.subheader("📚 Performance by Topic")
        topic_avg = df.groupby("topic")["score_pct"].mean().round().reset_index()
        topic_avg.columns = ["Topic", "Avg Score (%)"]
        st.bar_chart(topic_avg.set_index("Topic"))

    st.markdown("---")
    st.subheader("🗂️ Recent Quiz Attempts")

    display_df = df[["date", "topic", "score", "total_questions", "score_pct"]].copy()
    display_df.columns = ["Date", "Topic", "Score", "Total", "Percentage (%)"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
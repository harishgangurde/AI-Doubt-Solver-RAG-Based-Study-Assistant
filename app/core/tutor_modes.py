import streamlit as st

mode = st.selectbox("Select Mode", ["Beginner", "Intermediate", "Interview"])

def modify_prompt(answer, mode):
    if mode == "Beginner":
        return f"Explain simply: {answer}"
    elif mode == "Interview":
        return f"Give concise professional answer: {answer}"
    return answer
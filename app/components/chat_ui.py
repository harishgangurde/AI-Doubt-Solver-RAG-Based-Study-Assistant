import streamlit as st
import time

def stream_response(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.02)

def show_chat(messages):
    for role, msg in messages:
        with st.chat_message(role):
            if role == "ai":
                st.write_stream(stream_response(msg))
            else:
                st.write(msg)
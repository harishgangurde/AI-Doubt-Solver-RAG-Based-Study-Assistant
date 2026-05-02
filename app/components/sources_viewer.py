import streamlit as st

def show_sources(chunks):
    st.subheader("📄 Sources Used")
    for i, chunk in enumerate(chunks):
        with st.expander(f"Source {i+1}"):
            st.write(chunk["content"])
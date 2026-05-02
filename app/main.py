import sys
sys.path.insert(0, '.')

import streamlit as st
from app.components.auth import show_auth_page
from app.components.sidebar import show_sidebar
from app.utils.helpers import init_session_state, is_logged_in
from app.core.pdf_processor import process_and_store_pdf, get_user_documents, delete_document

st.set_page_config(
    page_title="AI Doubt Solver",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    init_session_state()

    if not is_logged_in():
        show_auth_page()
        return

    show_sidebar()

    st.title("🎓 AI Doubt Solver")
    st.markdown("Upload your study material and let AI help you learn smarter.")

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📄 Upload New Document")

        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Upload your textbook, notes, or any study material"
        )

        subject = st.text_input(
            "Subject / Topic name",
            placeholder="e.g. Data Structures, Machine Learning..."
        )

        if st.button("Upload & Process", type="primary", use_container_width=True):
            if not uploaded_file:
                st.warning("Please select a PDF file first.")
            elif not subject.strip():
                st.warning("Please enter a subject name.")
            else:
                with st.spinner("Processing PDF... this may take a minute ⏳"):
                    try:
                        result = process_and_store_pdf(
                            uploaded_file,
                            st.session_state.user_id,
                            subject
                        )
                        st.success(f"✅ Uploaded! {result['total_chunks']} chunks stored.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    with col2:
        st.subheader("📚 Your Documents")

        docs = get_user_documents(st.session_state.user_id)

        if not docs:
            st.info("No documents uploaded yet. Upload a PDF to get started!")
        else:
            for doc in docs:
                with st.container():
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        is_selected = st.session_state.selected_document_id == doc["id"]
                        label = f"{'✅ ' if is_selected else '📄 '}{doc['file_name']}"
                        st.markdown(f"**{label}**")
                        st.caption(f"Subject: {doc['subject']} | Chunks: {doc['total_chunks']}")

                    with col_b:
                        if st.button("Select", key=f"sel_{doc['id']}", use_container_width=True):
                            st.session_state.selected_document = doc["file_name"]
                            st.session_state.selected_document_id = doc["id"]
                            st.session_state.chat_history = []
                            st.session_state.chat_session_id = None
                            st.success(f"Selected: {doc['file_name']}")
                            st.rerun()

                        if st.button("🗑️", key=f"del_{doc['id']}", use_container_width=True):
                            delete_document(doc["id"], st.session_state.user_id)
                            if st.session_state.selected_document_id == doc["id"]:
                                st.session_state.selected_document = None
                                st.session_state.selected_document_id = None
                            st.rerun()

                    st.markdown("---")

    # Bottom stats
    if st.session_state.selected_document:
        st.info(f"📖 Active document: **{st.session_state.selected_document}** — Go to a page from the sidebar to start learning!")

if __name__ == "__main__":
    main()
import sys
sys.path.insert(0, '.')

import streamlit as st
from app.database.supabase_client import get_supabase

def show_sidebar():
    with st.sidebar:
        st.markdown("### 🎓 AI Doubt Solver")
        st.markdown("---")

        if st.session_state.get("user"):
            email = st.session_state.user.email
            st.markdown(f"👤 **{email}**")

        if st.session_state.get("selected_document"):
            st.success(f"📖 {st.session_state.selected_document}")
        else:
            st.warning("No document selected")

        st.markdown("---")
        st.markdown("### 📌 Navigation")
        st.markdown("🏠 [Home](/)")
        st.markdown("💬 [Doubt Solver](/doubt_solver)")
        st.markdown("📝 [Quiz Generator](/quiz)")
        st.markdown("🃏 [Flashcards](/flashcards)")
        st.markdown("📊 [Dashboard](/dashboard)")

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            try:
                supabase = get_supabase()
                supabase.auth.sign_out()
            except:
                pass
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
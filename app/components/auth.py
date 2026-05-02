import sys
sys.path.insert(0, '.')

import streamlit as st
from app.database.supabase_client import get_supabase

def show_auth_page():
    st.title("🎓 AI Doubt Solver")
    st.markdown("Your personal AI-powered study assistant.")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Welcome back!")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary", use_container_width=True):
            if not email or not password:
                st.warning("Please fill in all fields.")
            else:
                try:
                    supabase = get_supabase()
                    response = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    st.session_state.user = response.user
                    st.session_state.user_id = str(response.user.id)
                    st.success("Logged in successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")

    with tab2:
        st.subheader("Create your account")
        full_name = st.text_input("Full Name", key="signup_name")
        email_signup = st.text_input("Email", key="signup_email")
        password_signup = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

        if st.button("Sign Up", type="primary", use_container_width=True):
            if not all([full_name, email_signup, password_signup, confirm_password]):
                st.warning("Please fill in all fields.")
            elif password_signup != confirm_password:
                st.error("Passwords do not match.")
            elif len(password_signup) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                try:
                    supabase = get_supabase()
                    response = supabase.auth.sign_up({
                        "email": email_signup,
                        "password": password_signup
                    })

                    # Save profile
                    supabase_admin = get_supabase()
                    supabase_admin.table("profiles").insert({
                        "id": str(response.user.id),
                        "email": email_signup,
                        "full_name": full_name
                    }).execute()

                    st.success("Account created! Please check your email to verify, then login.")
                except Exception as e:
                    st.error(f"Sign up failed: {str(e)}")

import streamlit as st
from src.core.auth import AuthManager

def render_login_page():
    st.markdown("<h1 style='text-align: center;'>🔐 AI Book Analyzer Login</h1>", unsafe_allow_html=True)
    
    auth_manager = AuthManager()
    
    tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Guest Access"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                user = auth_manager.login_user(email, password)
                if user:
                    st.success("Login successful!")
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
                    
    with tab2:
        with st.form("signup_form"):
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit_reg = st.form_submit_button("Create Account")
            
            if submit_reg:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, msg = auth_manager.register_user(new_email, new_password)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                        
    with tab3:
        st.write("Access basic features without an account.")
        if st.button("Continue as Guest"):
            st.session_state.user = auth_manager.guest_login()
            st.rerun()

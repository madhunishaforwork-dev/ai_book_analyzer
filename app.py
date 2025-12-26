import sys
# Updated for deployment
import os
import streamlit as st

# Add the project root to python path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from src.ui import layout
    from src.ui.auth_ui import render_login_page
except ModuleNotFoundError as e:
    st.error(f"Startup Error: {e}")
    st.info("Debugging Info:")
    st.write(f"Root Directory: `{root_dir}`")
    try:
        st.write(f"Files in Root: `{os.listdir(root_dir)}`")
        if 'src' in os.listdir(root_dir):
             st.write(f"Files in src: `{os.listdir(os.path.join(root_dir, 'src'))}`")
    except Exception as dir_err:
        st.write(f"Error reading directories: {dir_err}")
    st.stop()

def main():
    if 'user' not in st.session_state:
        render_login_page()
    else:
        layout.main()

if __name__ == "__main__":
    main()

import streamlit as st
import os
from auth import login, logout, signup, check_auth, initialize_users
from utils.project_tasks import initialize_files
from streamlit_cookies_controller import CookieController
from utils.ai_chat import initialize_chat_state, render_chat_button, display_chat_ui
st.set_page_config(page_title="Growth Mindset App", page_icon="🚀", layout="wide")

# Initialize all required files
initialize_files()
initialize_users()

def main():

    # Initialize cookie controller
    cookie_controller = CookieController()

    # Check authentication status
    is_authenticated = check_auth()

    if not is_authenticated:
        auth_options = st.sidebar.radio("Choose an option", ["Login", "Signup"])

        if auth_options == "Login" and login():
            st.rerun()
        elif auth_options == "Signup":
            signup()
    else:
        st.sidebar.title("Navigation 🧭")
        page = st.sidebar.radio("Go to ", ["Home", "Tasks", "Projects", "Journal"])
        logout()

        if(page == "Home"):
            import page.home as home
            home.show()
        elif(page == "Tasks"):
            import page.tasks as tasks
            tasks.show()
        elif(page == "Projects"):
            import page.projects as projects
            projects.show()
        elif(page == "Journal"):
            import page.journal as journal
            journal.show()

    # Initialize chat state
    initialize_chat_state()

    # Render the chat button and UI
    render_chat_button()
    display_chat_ui()

if __name__ == "__main__":
    main()

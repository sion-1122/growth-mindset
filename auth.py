import streamlit as st
import pandas as pd
import bcrypt
from typing import Optional
import jwt
import datetime
import os
from datetime import timedelta
from streamlit_cookies_controller import CookieController
from dataclasses import dataclass

# Add User class definition
@dataclass
class User:
    username: str
    name: str
    password: str

# Use an environment variable for the secret key in production
SECRET_KEY = "your-secret-key-here"  # In production, use os.environ.get('SECRET_KEY')

# Initialize the cookie controller
cookie_controller = CookieController()

USERS_FILE = "data/users.csv"

def initialize_users() -> None:
    """Initialize users.csv file if it doesn't exist"""
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")

    # Create users.csv with required columns if it doesn't exist
    if not os.path.exists(USERS_FILE):
        # Create empty DataFrame with required columns
        users_df = pd.DataFrame(columns=["username", "name", "password"])

        # Create a default admin user
        admin_password = bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode()
        default_user = pd.DataFrame({
            "username": ["admin"],
            "name": ["Administrator"],
            "password": [admin_password]
        })

        # Add default admin user
        users_df = pd.concat([users_df, default_user], ignore_index=True)

        # Save to CSV
        users_df.to_csv(USERS_FILE, index=False)

def load_users():
    initialize_users()  # Ensure users file exists before loading
    return pd.read_csv(USERS_FILE)

def check_password(stored_password: str, provided_password: str):
    return bcrypt.checkpw(provided_password.encode(), stored_password.encode())

def get_user(username: str):
    users = load_users()
    user_row = users[users["username"] == username]
    if not user_row.empty:
        return User(
            username=user_row.iloc[0]["username"],
            name=user_row.iloc[0]["name"],
            password=user_row.iloc[0]["password"]
        )
    return None

def create_token(user_id: str) -> str:
    """Create a JWT token for the user"""
    expiration = datetime.datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
    return jwt.encode(
        {
            'user_id': user_id,
            'exp': expiration
        },
        SECRET_KEY,
        algorithm='HS256'
    )

def verify_token(token: str) -> Optional[str]:
    """Verify the JWT token and return the user_id if valid"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload.get('user_id')
    except:
        return None

def check_auth():
    """Check if user is authenticated"""
    # First check if we have auth state
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    # If not authenticated, check for token in cookies
    if not st.session_state['authenticated']:
        token = cookie_controller.get('auth_token')
        if token:
            user_id = verify_token(token)
            if user_id:
                user = get_user(user_id)
                if user:
                    st.session_state['authenticated'] = True
                    st.session_state['user_id'] = user_id
                    st.session_state['username'] = user.username
                    return True

    return st.session_state['authenticated']

def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        user: Optional[User] = get_user(username)

        if user and check_password(user.password, password):
            # Create token
            token = create_token(user.username)

            # Set cookie with 7 days expiration
            expiry = datetime.datetime.now() + timedelta(days=7)
            cookie_controller.set(
                'auth_token',
                token,
                expires=expiry  # Changed from integer timestamp to datetime object
            )

            # Set session state
            st.session_state["authenticated"] = True
            st.session_state["user_id"] = user.username
            st.session_state["username"] = username

            st.sidebar.success(f"Welcome, {user.name}! 🚀")
            return True
        else:
            st.sidebar.error("Invalid username or password")
    return False

def logout():
    if st.sidebar.button("Logout"):
        # Clear cookie
        cookie_controller.remove('auth_token')

        # Clear session state
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = None
        st.session_state["username"] = None

        st.rerun()

def signup():
    st.sidebar.title("Signup")

    new_username: str = st.sidebar.text_input("Username")
    new_name: str = st.sidebar.text_input("Name")
    new_password: str = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Create Account"):
        users: pd.DataFrame = load_users()
        if new_username in users["username"].values:
            st.sidebar.error("Username already exists")
        else:
            hashed_password: str= bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            new_user = pd.DataFrame({"username": [new_username], "name": [new_name], "password": [hashed_password]})
            users = pd.concat([users, new_user], ignore_index=True)
            users.to_csv(USERS_FILE, index=False)
            st.sidebar.success("Account created successfully! 🚀")

from typing import List
from pydantic import BaseModel, Field
from datetime import datetime
import streamlit as st
from streamlit_chat import message
import google.generativeai as genai
from utils.journal import load_journal_for_user
from utils.prompts import SYSTEM_PROMPT
from streamlit_elements import elements, html


# Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

class ChatMessage(BaseModel):
    """Model for chat messages"""
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.now)

def initialize_chat_state():
    """Initialize chat state in Streamlit session"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_visible" not in st.session_state:
        st.session_state.chat_visible = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = model.start_chat(history=[])

def toggle_chat():
    """Toggle chat visibility"""
    st.session_state.chat_visible = not st.session_state.chat_visible

def display_chat_ui():
    """Display the chat interface"""
    if not st.session_state.chat_visible:
        return

    st.markdown("""
    <style>
    .chat-container {
        position: fixed;
        bottom: 80px;
        right: 20px;
        width: 350px;
        height: 500px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        z-index: 1000;
        padding: 20px;
        overflow-y: auto;
    }
    .stTextInput {
        position: fixed;
        bottom: 100px;
        width: 310px;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        # Display chat messages
        for msg in st.session_state.messages:
            message(msg.content, is_user=(msg.role == "user"))

        # Chat input
        if prompt := st.text_input("Message JournalAI", key="chat_input"):
            # Add user message
            user_msg = ChatMessage(role="user", content=prompt)
            st.session_state.messages.append(user_msg)

            # Generate AI response
            response = generate_ai_response(prompt, st.session_state.user_id)
            ai_msg = ChatMessage(role="assistant", content=response)
            st.session_state.messages.append(ai_msg)

            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

def generate_ai_response(prompt: str, user_id: str) -> str:
    try:
        # Load user's recent journal entries
        journal_entries = load_journal_for_user(user_id)

        # Create context from recent entries
        recent_entries = journal_entries.tail(3).to_dict('records')
        context = "\n".join([f"Entry: {entry['content']}" for entry in recent_entries])

        # Prepare the prompt with context
        full_prompt = f"""
        {SYSTEM_PROMPT}

        Recent journal context:
        {context}

        User message: {prompt}
        """

        # Generate response using Gemini
        response = st.session_state.chat_history.send_message(full_prompt)
        return response.text

    except Exception as e:
        return f"I apologize, but I'm having trouble processing your request. Please try again later. Error: {str(e)}"

def render_chat_button():
    """Render the floating chat button"""
    with elements("chat_button"):
        html.button("💭",
            onClick=lambda: toggle_chat(),
            style={
                "position": "fixed",
                "bottom": "20px",
                "right": "20px",
                "width": "50px",
                "height": "50px",
                "borderRadius": "25px",
                "background": "#0066ff",
                "color": "white",
                "border": "none",
                "cursor": "pointer",
                "fontSize": "24px",
                "boxShadow": "0 2px 5px rgba(0,0,0,0.2)",
                "zIndex": "1000"
            }
        )

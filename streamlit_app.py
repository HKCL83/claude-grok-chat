import streamlit as st
from anthropic import Anthropic
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Page config
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize API keys from secrets
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
GROK_API_KEY = st.secrets["GROK_API_KEY"]

def get_grok_response(prompt, system_message="You are a real-time news assistant."):
    # ... (keep existing function implementation)
    pass

def get_claude_response(prompt, system_message="You are a versatile AI assistant.", files=None):
    # ... (keep existing function implementation)
    pass

def get_image(prompt):
    # ... (keep existing function implementation)
    pass

# Title
st.title("AI Assistant")

# Initialize conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Display chat history
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.conversation.append({"role": "user", "content": prompt})

    try:
        if "latest news" in prompt.lower() or "current events" in prompt.lower():
            news_response = get_grok_response(prompt, "You are a real-time news assistant.")
            st.chat_message("assistant").markdown(news_response)
            st.session_state.conversation.append({"role": "assistant", "content": news_response})
        elif "render image" in prompt.lower() or "generate image" in prompt.lower():
            image_response = get_image(prompt)
            st.chat_message("assistant").markdown(f"Image generated: {image_response}")
            st.session_state.conversation.append({"role": "assistant", "content": image_response})
        else:
            claude_response = get_claude_response(prompt, files=uploaded_files if 'uploaded_files' in locals() else None)
            st.chat_message("assistant").markdown(claude_response)
            st.session_state.conversation.append({"role": "assistant", "content": claude_response})
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Create a container for bottom controls
with st.container():
    col1, col2 = st.columns([3, 1])
    
    # File uploader in the left column
    with col1:
        uploaded_files = st.file_uploader(
            "Upload Files",
            type=["png", "jpg", "jpeg", "txt", "pdf", "doc", "docx", "csv"],
            accept_multiple_files=True,
            key="file_uploader"
        )
    
    # Clear button in the right column
    with col2:
        if st.button("Clear Chat", key="clear_button", help="Clear the chat history"):
            st.session_state.conversation = []
            st.rerun()

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

# Create the main container for the chat interface
main_container = st.container()
bottom_container = st.container()

with main_container:
    # Title
    st.title("AI Assistant")

    # Initialize conversation history
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display chat history
    chat_placeholder = st.empty()
    with chat_placeholder.container():
        for message in st.session_state.conversation:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# Create a container for the bottom elements that will be fixed
with bottom_container:
    # Add some vertical space to push the input to the bottom
    st.markdown(
        """
        <style>
        .stChatFloatingInputContainer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: white;
            padding: 1rem;
            z-index: 100;
        }
        .main-container {
            margin-bottom: 150px;  /* Adjust based on your bottom container height */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Create columns for the file uploader and clear button
    col1, col2 = st.columns([4, 1])
    
    # File uploader
    with col1:
        uploaded_files = st.file_uploader(
            "",  # Empty label to reduce vertical space
            type=["png", "jpg", "jpeg", "txt", "pdf", "doc", "docx", "csv"],
            accept_multiple_files=True,
            key="file_uploader"
        )
    
    # Clear button
    with col2:
        if st.button("Clear Chat", key="clear_button"):
            st.session_state.conversation = []
            st.rerun()

    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        with main_container:
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

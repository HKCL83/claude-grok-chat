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
    layout="centered"
)

# Custom CSS to hide the duplicate "Drag and drop files here" text
st.markdown("""
    <style>
    /* Hide the duplicate drag and drop text */
    [data-testid="stFileUploadDropzone"] > div:first-child {
        display: none;
    }
    
    /* Ensure buttons are aligned */
    .stButton {
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize API keys from secrets
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
GROK_API_KEY = st.secrets["GROK_API_KEY"]

[... keep all your existing functions ...]

# Create main container
main_container = st.container()

with main_container:
    # Title
    st.title("AI Assistant")

    # Initialize conversation history
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display chat history
    for message in st.session_state.conversation:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Add vertical space to push content to bottom
    st.markdown("<div style='min-height: calc(100vh - 400px);'></div>", unsafe_allow_html=True)

    # Chat input
    prompt = st.chat_input("What would you like to know?")

    # File uploader and Clear Chat in columns
    col1, col2 = st.columns([4,1])
    
    with col1:
        uploaded_files = st.file_uploader(
            " ",  # Empty label to remove extra text
            type=["png", "jpg", "jpeg", "txt", "pdf", "doc", "docx", "csv"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.conversation = []
            st.rerun()

    # Handle the prompt
    if prompt:
        st.chat_message("user").markdown(prompt)
        st.session_state.conversation.append({"role": "user", "content": prompt})

        try:
            if "latest news" in prompt.lower() or "current events" in prompt.lower():
                news_response = get_grok_response(prompt)
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

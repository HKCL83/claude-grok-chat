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

# Custom CSS for styling
st.markdown("""
    <style>
    /* Set the main background color */
    .stApp {
        background-color: #4dacbc;
    }
    
    /* Create a scrollable container for chat messages */
    .chat-container {
        height: calc(100vh - 250px);  /* Adjust height to leave space for input */
        overflow-y: auto;
        margin-bottom: 10px;
        padding-right: 10px;
    }
    
    /* Style chat message containers */
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    
    /* Fix input area at the bottom */
    .fixed-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #4dacbc;
        padding: 1rem;
        z-index: 1000;
    }
    
    /* Style input container and file uploader */
    .stChatInputContainer, [data-testid="stFileUploadDropzone"] {
        background-color: white !important;
        border-radius: 10px;
    }
    
    /* Hide duplicate drag and drop text */
    [data-testid="stFileUploadDropzone"] > div:first-child {
        display: none;
    }
    
    /* Align buttons */
    .stButton {
        margin-top: 0.5rem;
    }

    /* Make buttons have white background */
    .stButton button {
        background-color: white !important;
    }

    /* Add padding at the bottom for fixed input area */
    .main-content {
        padding-bottom: 200px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize API keys from secrets
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
GROK_API_KEY = st.secrets["GROK_API_KEY"]

[... keep all your existing functions unchanged ...]

# Create a container for the main content
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Create scrollable container for chat history
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
chat_container = st.container()

# Display chat history in the scrollable container
with chat_container:
    # Initialize conversation history
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display existing messages
    for message in st.session_state.conversation:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

st.markdown('</div>', unsafe_allow_html=True)

# Close main content div
st.markdown('</div>', unsafe_allow_html=True)

# Fixed input area at the bottom
st.markdown('<div class="fixed-bottom">', unsafe_allow_html=True)
input_container = st.container()

with input_container:
    # Chat input
    prompt = st.chat_input("What would you like to know?")

    # File uploader and Clear Chat in columns
    col1, col2 = st.columns([4,1])
    
    with col1:
        uploaded_files = st.file_uploader(
            " ",
            type=["png", "jpg", "jpeg", "txt", "pdf", "doc", "docx", "csv"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.conversation = []
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Handle the prompt (keep this outside the fixed area but still functional)
if prompt:
    with chat_container:
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

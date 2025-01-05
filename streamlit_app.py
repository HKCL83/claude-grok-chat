import streamlit as st
from anthropic import Anthropic
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import base64
from io import BytesIO

# Custom CSS to match Claude's interface
st.markdown("""
    <style>
    /* Overall app styling */
    .stApp {
        background-color: #1a1b1e;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu, header, footer {
        visibility: hidden;
    }
    
    /* Input container styling */
    .input-container {
        position: fixed;
        top: 20px;
        left: 0;
        right: 0;
        padding: 20px;
        background-color: #1a1b1e;
        z-index: 1000;
    }
    
    /* Chat input styling */
    .stTextInput > div > div > input {
        background-color: #2d2e33 !important;
        color: #9ca3af !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 15px !important;
        font-size: 16px !important;
    }
    
    /* Plus button styling */
    .plus-button {
        background-color: #2d2e33 !important;
        color: #ffffff !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        padding: 0 !important;
        font-size: 24px !important;
        line-height: 38px !important;
        border: none !important;
        cursor: pointer !important;
    }
    
    /* File upload area styling */
    .stUploadButton {
        background-color: #2d2e33 !important;
        border-radius: 10px !important;
        padding: 20px !important;
        margin-top: 10px !important;
    }
    
    .upload-text {
        color: #ffffff;
        font-size: 14px;
        margin-top: 5px;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: #2d2e33;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Streamlit
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize API clients
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
GROK_API_KEY = st.secrets["GROK_API_KEY"]

# Input area at the top
input_container = st.container()
with input_container:
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input("", placeholder="What would you like to know?", key="chat_input")
    
    with col2:
        if st.button("+", key="plus_button", help="Upload files"):
            st.session_state.show_upload = True

# File upload area
if 'show_upload' not in st.session_state:
    st.session_state.show_upload = False

if st.session_state.show_upload:
    upload_container = st.container()
    with upload_container:
        st.markdown("""
            <div class="upload-text">
                Drag and drop files here<br>
                <span style="color: #9ca3af; font-size: 12px;">
                    Limit 200MB per file • PNG, JPG, JPEG, PDF, TXT, DOC, DOCX
                </span>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "",
            type=['png', 'jpg', 'jpeg', 'pdf', 'txt', 'doc', 'docx'],
            accept_multiple_files=True,
            key="file_uploader",
            label_visibility="collapsed"
        )

# Rest of your existing functions (process_uploaded_file, get_grok_response, get_claude_response)
[Your existing function implementations here]

# Chat history display
chat_container = st.container()
with chat_container:
    for message in st.session_state.get('conversation', []):
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Process user input
if user_input:
    with chat_container:
        st.chat_message("user").write(user_input)
        
        try:
            # Enhanced query detection
            if any(keyword in user_input.lower() for keyword in ['weather', 'news', 'current events']):
                response = get_grok_response(user_input)
            else:
                response = get_claude_response(user_input)
            
            st.chat_message("assistant").write(response)
            
            if 'conversation' not in st.session_state:
                st.session_state.conversation = []
            st.session_state.conversation.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response}
            ])
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Clear chat button at the bottom
if st.button("Clear Chat"):
    st.session_state.conversation = []
    st.rerun()
import streamlit as st
from anthropic import Anthropic
import requests
import json
from datetime import datetime
import os
from PIL import Image
import io
import base64

# Page config
st.set_page_config(
    page_title="Claude",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS to match the screenshot aesthetics
st.markdown("""
<style>
    /* Main container */
    .main {
        background-color: #1E1E1E;
        color: white;
        padding: 0;
    }
    
    /* Header styling */
    .stMarkdown h1 {
        font-family: serif;
        color: white;
        font-size: 24px;
        padding: 10px 0;
        margin: 0;
    }
    
    /* Chat container */
    .stChatMessage {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    
    /* Input box styling */
    .stChatInputContainer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 20px;
        background-color: #1E1E1E;
        border-top: 1px solid #333;
    }
    
    /* Upload button styling */
    .stUploadButton {
        color: #FF6B4A !important;
        border-color: #FF6B4A !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Top navigation bar */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        background-color: #1E1E1E;
        border-bottom: 1px solid #333;
    }
    
    .back-button {
        color: #FF6B4A;
        text-decoration: none;
        font-size: 16px;
    }
    
    .title {
        color: white;
        font-size: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize API client
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# Custom navigation
st.markdown("""
    <div class="top-nav">
        <a href="#" class="back-button">‹ Chats</a>
        <span class="title">Claude 3.5 Sonnet</span>
        <span></span>
    </div>
""", unsafe_allow_html=True)

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "How can I help you this evening?"
    })

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# File uploader for documents and images
uploaded_file = st.file_uploader("", 
    type=["txt", "pdf", "png", "jpg", "jpeg", "csv", "xlsx"],
    label_visibility="collapsed")

if uploaded_file is not None:
    # Handle different file types
    file_type = uploaded_file.type
    if file_type.startswith('image'):
        # Handle image files
        image = Image.open(uploaded_file)
        st.image(image, caption=uploaded_file.name)
        
        # Add image to message history
        st.session_state.messages.append({
            "role": "user",
            "content": f"[Uploaded image: {uploaded_file.name}]"
        })
    else:
        # Handle document files
        file_contents = uploaded_file.read()
        
        # Add document to message history
        st.session_state.messages.append({
            "role": "user",
            "content": f"[Uploaded document: {uploaded_file.name}]"
        })

# Chat input
if prompt := st.chat_input("Chat with Claude", key="chat_input"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    # Get Claude's response
    try:
        messages = [
            {"role": m["role"], "content": m["content"]} 
            for m in st.session_state.messages[-5:]
        ]
        
        response = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=messages
        )
        
        assistant_response = response.content[0].text
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_response
        })
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.write(assistant_response)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Clear chat button (hidden in UI but accessible via command)
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
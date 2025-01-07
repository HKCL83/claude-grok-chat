import streamlit as st
from anthropic import Anthropic
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import io

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
    # ... (keep existing function as is)
    pass

def get_claude_response(prompt, system_message="You are a versatile AI assistant.", files=None):
    messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.conversation[-5:]] if "conversation" in st.session_state else []
    
    # If files are uploaded, include them in the message
    if files:
        file_contents = []
        for file in files:
            file_content = file.read()
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8', errors='ignore')
            file_contents.append({
                "filename": file.name,
                "content": file_content
            })
        
        # Add file information to the prompt
        file_info = "\n".join([f"File: {f['filename']}\nContent:\n{f['content']}" for f in file_contents])
        prompt = f"Files uploaded:\n{file_info}\n\n{prompt}"
    
    messages.append({"role": "user", "content": prompt})
    
    response = anthropic.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        system=system_message,
        messages=messages
    )
    
    return response.content[0].text if isinstance(response.content, list) else response.content

def get_image(prompt):
    # ... (keep existing function as is)
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

# Create a container for the input area
input_container = st.container()

# Create three columns for the buttons
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # File uploader for images
    uploaded_images = st.file_uploader(
        "Upload Images",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="image_uploader"
    )

with col2:
    # File uploader for documents
    uploaded_files = st.file_uploader(
        "Upload Documents",
        type=["txt", "pdf", "doc", "docx", "csv"],
        accept_multiple_files=True,
        key="doc_uploader"
    )

with col3:
    # Clear chat button
    if st.button("Clear Chat", key="clear_button"):
        st.session_state.conversation = []
        st.rerun()

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.conversation.append({"role": "user", "content": prompt})

    try:
        # Combine all uploaded files
        all_files = (uploaded_images or []) + (uploaded_files or [])
        
        if "latest news" in prompt.lower() or "current events" in prompt.lower():
            news_response = get_grok_response(prompt, "You are a real-time news assistant.")
            st.chat_message("assistant").markdown(news_response)
            st.session_state.conversation.append({"role": "assistant", "content": news_response})
        elif "render image" in prompt.lower() or "generate image" in prompt.lower():
            image_response = get_image(prompt)
            st.chat_message("assistant").markdown(f"Image generated: {image_response}")
            st.session_state.conversation.append({"role": "assistant", "content": image_response})
        else:
            claude_response = get_claude_response(prompt, files=all_files)
            st.chat_message("assistant").markdown(claude_response)
            st.session_state.conversation.append({"role": "assistant", "content": claude_response})
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

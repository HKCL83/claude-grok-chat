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

# ... (Keep the existing functions as is)

# Title
st.title("AI Assistant")

# Initialize conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Display chat history
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input with file upload
prompt = st.chat_input("What would you like to know or upload?")

# Add context options
st.write("---")
st.write("Add Context")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Camera"):
        st.write("Camera functionality would be implemented here")

with col2:
    if st.button("Photos"):
        uploaded_file = st.file_uploader("Choose a photo", type=["jpg", "jpeg", "png"], key="photo_uploader")
        if uploaded_file is not None:
            # Handle photo upload
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
            st.write(f"Photo uploaded: {file_details['FileName']}")
            st.session_state.conversation.append({"role": "user", "content": f"User uploaded a photo: {file_details['FileName']}"})

with col3:
    if st.button("Files"):
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"], key="file_uploader")
        if uploaded_file is not None:
            # Handle file upload
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
            st.write(f"File uploaded: {file_details['FileName']}")
            st.session_state.conversation.append({"role": "user", "content": f"User uploaded a file: {file_details['FileName']}"})

if prompt:
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
            claude_response = get_claude_response(prompt)
            st.chat_message("assistant").markdown(claude_response)
            st.session_state.conversation.append({"role": "assistant", "content": claude_response})
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.conversation = []
    st.rerun()
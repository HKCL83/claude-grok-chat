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
    # ... (Keep the existing function as is)

def get_claude_response(prompt, system_message="You are a versatile AI assistant."):
    # ... (Keep the existing function as is)

def get_image(prompt):
    # This function is a placeholder for when you have an actual image generation API from Grok
    return "Image would be generated here if API was available."

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
file_uploader = st.file_uploader("Upload an image or file", type=["jpg", "jpeg", "png", "pdf"])

if prompt or file_uploader:
    if prompt:
        st.chat_message("user").markdown(prompt)
        st.session_state.conversation.append({"role": "user", "content": prompt})
    elif file_uploader:
        # Handle file upload
        file_details = {"FileName": file_uploader.name, "FileType": file_uploader.type}
        st.chat_message("user").markdown(f"User uploaded a file: {file_details['FileName']}")
        st.session_state.conversation.append({"role": "user", "content": f"User uploaded a file: {file_details['FileName']}"})

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
            if file_uploader:
                # Here you might want to process the file. Since we can't actually execute code or generate images:
                file_response = f"File {file_uploader.name} has been uploaded and could be processed here."
                st.chat_message("assistant").markdown(file_response)
                st.session_state.conversation.append({"role": "assistant", "content": file_response})
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
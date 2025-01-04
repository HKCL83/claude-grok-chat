import streamlit as st
from anthropic import Anthropic
import requests
import json
from datetime import datetime
import base64
from dotenv import load_dotenv

# Page config
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Initialize API keys from secrets
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
GROK_API_KEY = st.secrets["GROK_API_KEY"]

# Cache the get_grok_response function to improve efficiency
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_grok_response(prompt, system_message="You are a real-time news assistant."):
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    messages = [
        {
            "role": "system",
            "content": f"""You are a real-time news assistant. When reporting news:
            1. Only report verifiable current news from {today}
            2. If you cannot verify a story is from today, say so explicitly
            3. Include the source name (e.g., Reuters, AP, etc.) but not URLs unless you can verify them
            4. If you're not sure about the date, acknowledge the uncertainty
            5. Prioritize factual reporting over completeness
            
            Format: 
            [SOURCE NAME] [DATE IF KNOWN] - [HEADLINE] - [SUMMARY]"""
        }
    ]
    
    if "conversation" in st.session_state:
        messages.extend(st.session_state.conversations[st.session_state.current_convo][-5:])  # Limit to last 5 messages for efficiency
    
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    data = {
        "model": "grok-beta",
        "messages": messages,
        "stream": False,
        "temperature": 0.2,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"API request failed: {str(e)}"
    except KeyError:
        return "Unexpected response format from the API."

# Function to get Claude response
def get_claude_response(prompt, system_message="You are a versatile AI assistant."):
    messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.conversations[st.session_state.current_convo][-5:]] if "conversation" in st.session_state else []
    messages.append({"role": "user", "content": prompt})
    
    response = anthropic.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        system=system_message,
        messages=messages
    )
    
    return response.content[0].text if isinstance(response.content, list) else response.content

# Function to handle file upload
def handle_file_upload(uploaded_file):
    file_type = uploaded_file.type.split('/')[0]
    if file_type == 'image':
        # Convert image to base64 for potential API use
        file_content = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        return f"Image uploaded: {uploaded_file.name}"
    else:
        file_content = uploaded_file.getvalue().decode('utf-8')
        return f"File uploaded: {uploaded_file.name}"

# Title
st.title("AI Assistant")

# Initialize conversation history with multiple conversations
if "conversations" not in st.session_state:
    st.session_state.conversations = {"default": []}
if "current_convo" not in st.session_state:
    st.session_state.current_convo = "default"
if "memory" not in st.session_state:
    st.session_state.memory = {}

# UI for managing conversations
st.sidebar.title("Conversations")
current_convo = st.sidebar.selectbox(
    "Select Conversation",
    options=list(st.session_state.conversations.keys()),
    key="current_convo"
)

if st.sidebar.button("New Conversation"):
    new_convo_name = f"Conversation_{len(st.session_state.conversations)}"
    st.session_state.conversations[new_convo_name] = []
    st.session_state.current_convo = new_convo_name
    st.experimental_rerun()

if st.sidebar.button("Delete Current Conversation"):
    if len(st.session_state.conversations) > 1:
        del st.session_state.conversations[st.session_state.current_convo]
        st.session_state.current_convo = list(st.session_state.conversations.keys())[0]
        st.experimental_rerun()
    else:
        st.sidebar.warning("Cannot delete the last conversation.")

# File Uploader
uploaded_file = st.file_uploader("Choose a file or photo", type=["pdf", "jpg", "jpeg", "png", "txt"])

if uploaded_file is not None:
    file_upload_response = handle_file_upload(uploaded_file)
    st.chat_message("user").markdown(f"User uploaded: {uploaded_file.name}")
    st.chat_message("assistant").markdown(file_upload_response)
    st.session_state.conversations[st.session_state.current_convo].append({"role": "user", "content": f"User uploaded: {uploaded_file.name}"})
    st.session_state.conversations[st.session_state.current_convo].append({"role": "assistant", "content": file_upload_response})

# Display chat history for the current conversation
for message in st.session_state.conversations[st.session_state.current_convo]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.conversations[st.session_state.current_convo].append({"role": "user", "content": prompt})

    # Check for memory commands
    if prompt.startswith("!remember "):
        # Format: !remember key: value
        key_value = prompt[10:].split(':', 1)
        if len(key_value) == 2:
            key, value = key_value
            st.session_state.memory[key.strip()] = value.strip()
            response = f"Remembered: {key.strip()} - {value.strip()}"
        else:
            response = "Please use the format '!remember key: value'"
    elif prompt.startswith("!recall "):
        key = prompt[8:].strip()
        if key in st.session_state.memory:
            response = f"Recalled: {key} - {st.session_state.memory[key]}"
        else:
            response = f"No memory found for: {key}"
    else:
        # Your existing logic for AI responses
        try:
            if "latest news" in prompt.lower() or "current events" in prompt.lower():
                response = get_grok_response(prompt, "You are a real-time news assistant.")
            elif "render image" in prompt.lower() or "generate image" in prompt.lower():
                response = get_image(prompt)
            else:
                response = get_claude_response(prompt)
        except Exception as e:
            response = f"An error occurred: {str(e)}"

    st.chat_message("assistant").markdown(response)
    st.session_state.conversations[st.session_state.current_convo].append({"role": "assistant", "content": response})

# Clear Chat functionality for the current conversation
if st.button("Clear Current Conversation"):
    st.session_state.conversations[st.session_state.current_convo] = []
    st.experimental_rerun()

# Function for image generation placeholder
def get_image(prompt):
    # This function is a placeholder for when you have an actual image generation API from Grok
    return "Image would be generated here if API was available."
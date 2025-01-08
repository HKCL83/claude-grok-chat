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
    
    /* Style chat message containers */
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
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
    </style>
""", unsafe_allow_html=True)

# Initialize API keys from secrets
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
GROK_API_KEY = st.secrets["GROK_API_KEY"]

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
        messages.extend(st.session_state.conversation[-5:])
    
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
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

def get_claude_response(prompt, system_message="You are a versatile AI assistant.", files=None):
    messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.conversation[-5:]] if "conversation" in st.session_state else []
    
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
    return "Image would be generated here if API was available."

# Create main container for chat history
chat_container = st.container()

# Display chat history in the main container
with chat_container:
    # Initialize conversation history
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display existing messages
    for message in st.session_state.conversation:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Add space to push input to bottom
st.markdown("<div style='min-height: calc(100vh - 400px);'></div>", unsafe_allow_html=True)

# Chat input and controls container
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

    # Handle the prompt
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

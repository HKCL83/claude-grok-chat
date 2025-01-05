import streamlit as st
from anthropic import Anthropic
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import base64
from io import BytesIO

# Must be the first Streamlit command
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# Initialize API clients
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
GROK_API_KEY = st.secrets["GROK_API_KEY"]

def process_uploaded_file(uploaded_file):
    """Process uploaded file and return its content"""
    if uploaded_file is None:
        return None
    
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension in ['png', 'jpg', 'jpeg']:
        return {
            'type': 'image',
            'content': encode_image_to_base64(uploaded_file)
        }
    elif file_extension in ['pdf', 'txt', 'doc', 'docx']:
        try:
            content = uploaded_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            return {
                'type': 'document',
                'content': content
            }
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return None
    else:
        st.error("Unsupported file type")
        return None

def encode_image_to_base64(image_file):
    """Convert uploaded image to base64 string"""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def get_grok_response(prompt):
    """Get response from Grok API"""
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
            3. Include the source name (e.g., Reuters, AP, etc.) but not URLs
            4. If you're not sure about the date, acknowledge the uncertainty
            5. Prioritize factual reporting over completeness"""
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

def get_claude_response(prompt, files=None):
    """Get response from Claude API"""
    messages = [{"role": m["role"], "content": m["content"]} 
               for m in st.session_state.get('conversation', [])[-5:]]
    
    if files:
        file_contents = []
        for file in files:
            if file['type'] == 'image':
                file_contents.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": file['content']
                    }
                })
            elif file['type'] == 'document':
                file_contents.append({
                    "type": "text",
                    "text": file['content']
                })
        
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                *file_contents
            ]
        })
    else:
        messages.append({"role": "user", "content": prompt})
    
    response = anthropic.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=messages
    )
    
    return response.content[0].text if isinstance(response.content, list) else response.content

# Initialize session state for conversation if it doesn't exist
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

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
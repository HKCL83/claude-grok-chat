import streamlit as st
from anthropic import Anthropic
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import base64
from io import BytesIO

# Page config
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize API keys from secrets
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
GROK_API_KEY = st.secrets["GROK_API_KEY"]

def encode_image_to_base64(image_file):
    """Convert uploaded image to base64 string"""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def process_uploaded_file(uploaded_file):
    """Process uploaded file and return its content"""
    if uploaded_file is None:
        return None
    
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension in ['png', 'jpg', 'jpeg']:
        # Handle image files
        return {
            'type': 'image',
            'content': encode_image_to_base64(uploaded_file)
        }
    elif file_extension in ['pdf', 'txt', 'doc', 'docx']:
        # Handle document files
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
    
    # Handle file uploads in the message
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
        
        # Add file contents to the message
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
        system=system_message,
        messages=messages
    )
    
    return response.content[0].text if isinstance(response.content, list) else response.content

def get_image(prompt):
    """
    Placeholder for image generation functionality.
    This should be replaced with actual image generation API integration.
    """
    return "Image generation is not yet implemented."

# Title
st.title("AI Assistant")

# Initialize conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Custom CSS for the plus button
st.markdown("""
    <style>
    .stButton > button {
        border-radius: 50%;
        padding: 0px 13px;
        font-size: 24px;
        font-weight: lighter;
        margin: 0;
        height: 38px;
        line-height: 38px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize uploaded_files
uploaded_files = None

# Create a container for the input area
input_container = st.container()

# Create columns for input area: chat input, plus button
col1, col2 = input_container.columns([6, 1])

with col1:
    prompt = st.chat_input("What would you like to know?")

with col2:
    # Plus button for file upload
    if st.button("+"):
        st.session_state.show_uploader = True

# Show file uploader if button was clicked
if 'show_uploader' not in st.session_state:
    st.session_state.show_uploader = False
    
if st.session_state.show_uploader:
    uploaded_files = st.file_uploader(
        "Drag and drop files here",
        type=['png', 'jpg', 'jpeg', 'pdf', 'txt', 'doc', 'docx'],
        accept_multiple_files=True,
        key="file_uploader"
    )

# Process uploaded files only if files were uploaded
if uploaded_files:
        st.session_state.show_uploader = False  # Hide uploader after files are selected

# Display chat history
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process uploaded files
processed_files = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        processed_file = process_uploaded_file(uploaded_file)
        if processed_file:
            processed_files.append(processed_file)

# Process chat input
if prompt:
    st.chat_message("user").markdown(prompt)
    
    # Add uploaded files to the message display
    if processed_files:
        with st.chat_message("user"):
            for file in processed_files:
                if file['type'] == 'image':
                    st.image(BytesIO(base64.b64decode(file['content'])))
                elif file['type'] == 'document':
                    st.text("Uploaded document: " + str(len(file['content'])) + " characters")
    
    st.session_state.conversation.append({"role": "user", "content": prompt})

    try:
        # Keywords that indicate current events or news queries
        news_keywords = [
            "latest news", "current events", "what's happening",
            "recent news", "today's news", "breaking news",
            "current situation", "latest updates", "news today",
            "what's going on", "recent developments",
            "weather", "forecast"  # Added weather-related keywords
        ]
        
        # Check if the prompt contains any news keywords
        is_news_query = any(keyword in prompt.lower() for keyword in news_keywords)
        
        if is_news_query:
            # Use Grok for current events, news, and weather queries
            news_response = get_grok_response(prompt)
            st.chat_message("assistant").markdown(news_response)
            st.session_state.conversation.append({"role": "assistant", "content": news_response})
        elif "render image" in prompt.lower() or "generate image" in prompt.lower():
            image_response = get_image(prompt)
            st.chat_message("assistant").markdown(f"Image generated: {image_response}")
            st.session_state.conversation.append({"role": "assistant", "content": image_response})
        else:
            # Use Claude for all other queries
            claude_response = get_claude_response(prompt, files=processed_files)
            st.chat_message("assistant").markdown(claude_response)
            st.session_state.conversation.append({"role": "assistant", "content": claude_response})
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.conversation = []
    st.rerun()
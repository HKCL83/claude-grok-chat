import streamlit as st
from anthropic import Anthropic
import requests
import json

# Page config
st.set_page_config(
    page_title="Enhanced AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize API keys from secrets
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
GROK_API_KEY = st.secrets["GROK_API_KEY"]

def get_grok_response(prompt, system_message="You are a helpful assistant with access to real-time information and current news."):
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "grok-beta",
        "messages": [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        if hasattr(response, 'text'):
            error_details = response.json()
            st.error(f"Error details: {error_details}")
        raise Exception(f"Grok API error: {str(e)}")

# Title
st.title("AI Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Check if this is a news request
        if any(word in prompt.lower() for word in ['news', 'headlines', 'current events']):
            news_prompt = """Provide only the latest, current news (from today or very recent). 
            Format each headline as:
            [DATE] - [HEADLINE] - [BRIEF SUMMARY]
            
            Original request: """ + prompt
            
            # Get Grok's response for news
            grok_response = get_grok_response(news_prompt)
            
            # Have Claude enhance the response
            claude_prompt = f"""Here is the latest news information: {grok_response}

            Please analyze this information and provide:
            1. Verification that these are actually current/recent events
            2. Additional context or background for key stories
            3. Any corrections if you notice outdated information
            4. Clear formatting with dates and headlines
            
            Original user request: {prompt}"""

        # Check if this is an image request
        elif any(word in prompt.lower() for word in ['image', 'picture', 'draw', 'generate']):
            grok_response = get_grok_response(f"Generate an image based on: {prompt}")
            claude_prompt = f"Here's what was generated: {grok_response}\n\nPlease describe and analyze this in detail."

        else:
            # Direct question to Claude
            claude_prompt = prompt

        # Get Claude's response
        response = anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            system="You are an advanced AI assistant. For news, verify currency and add context. For images, describe thoroughly. For general questions, be direct and helpful. Always maintain accuracy and clarity.",
            messages=[{
                "role": "user",
                "content": claude_prompt
            }]
        )
        
        # Extract just the text content
        assistant_response = response.content[0].text if isinstance(response.content, list) else response.content

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(assistant_response)
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
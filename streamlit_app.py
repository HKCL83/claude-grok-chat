import streamlit as st
from anthropic import Anthropic
import requests
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize API keys from secrets
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
GROK_API_KEY = st.secrets["GROK_API_KEY"]

def get_grok_response(prompt, system_message="You are a helpful assistant with real-time access to current information."):
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    data = {
        "model": "grok-beta",
        "messages": [
            {
                "role": "system",
                "content": f"You are a real-time news assistant. Only provide news from {today}. Do not reference historical events unless specifically asked."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "temperature": 0.2,  # Lower temperature for more focused responses
        "max_tokens": 500    # Reduced for faster response
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

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
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Check if this is a news request
        if any(word in prompt.lower() for word in ['news', 'headlines', 'current events']):
            today = datetime.now().strftime("%Y-%m-%d")
            news_prompt = f"""Provide ONLY today's ({today}) top news headlines. 
            Format each headline as:
            [TIME] - [HEADLINE] - [ONE-LINE SUMMARY]
            
            Provide exactly what was requested (e.g., if 5 headlines were asked for, provide exactly 5).
            Only include news from {today}."""
            
            grok_response = get_grok_response(news_prompt)
            
            # Direct output of Grok's response for news
            with st.chat_message("assistant"):
                st.markdown(grok_response)
            st.session_state.messages.append({"role": "assistant", "content": grok_response})

        else:
            # Handle non-news requests with Claude
            response = anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                system="You are a helpful AI assistant. Be direct and concise in your responses.",
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            assistant_response = response.content[0].text if isinstance(response.content, list) else response.content
            
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
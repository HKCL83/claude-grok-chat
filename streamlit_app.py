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

# Title
st.title("AI Assistant")

# Initialize conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Display chat history
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.conversation.append({"role": "user", "content": prompt})

    try:
        if any(word in prompt.lower() for word in ['news', 'headlines', 'current events']) or \
           any(word in prompt.lower() for word in ['these', 'this', 'those']):
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            if any(word in prompt.lower() for word in ['news', 'headlines', 'current events']):
                news_prompt = f"""Provide ONLY verified current news from major news sources.
                For each headline include:
                1. News source name
                2. Date if known (must be {today})
                3. Complete headline
                4. Brief factual summary
                
                Format each entry as:
                [SOURCE NAME] [DATE] - [HEADLINE] - [SUMMARY]
                
                If you cannot verify a story is from today, say so explicitly."""
            else:
                news_prompt = prompt + "\nProvide source names and dates for verification."
            
            grok_response = get_grok_response(news_prompt)
            
            st.chat_message("assistant").markdown(grok_response)
            st.session_state.conversation.append({"role": "assistant", "content": grok_response})

        else:
            messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.conversation[-5:]]
            messages.append({"role": "user", "content": prompt})
            
            response = anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                system="You are a helpful AI assistant. Remember context from our conversation and be direct in your responses.",
                messages=messages
            )
            
            assistant_response = response.content[0].text if isinstance(response.content, list) else response.content
            
            st.chat_message("assistant").markdown(assistant_response)
            st.session_state.conversation.append({"role": "assistant", "content": assistant_response})
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.conversation = []
    st.rerun()
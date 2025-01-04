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
            "content": f"""You are a real-time news assistant. For each headline:
            1. Only provide news from {today}
            2. Include the exact publication date and time
            3. Include the direct source URL
            4. Verify the date in the article matches today's date
            5. If asked about specific topics, ensure the news is recent and relevant
            Format: [DATE] [TIME] - [HEADLINE] - [SUMMARY] - Source: [URL]"""
        }
    ]
    
    if "conversation" in st.session_state:
        messages.extend(st.session_state.conversation[-5:])
    
    messages.append({
        "role": "user",
        "content": prompt + "\nPlease include source URLs and verify all dates are current."
    })
    
    data = {
        "model": "grok-beta",
        "messages": messages,
        "stream": False,
        "temperature": 0.2,
        "max_tokens": 1000  # Increased for source URLs
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
                news_prompt = f"""Provide ONLY verified news from {today}. 
                For each headline include:
                1. Exact publication date and time
                2. Complete headline
                3. Brief summary
                4. Direct source URL
                5. Verify that the article's content is from today
                
                Format each entry as:
                [DATE] [TIME] - [HEADLINE] - [SUMMARY] - Source: [URL]
                
                If searching for specific topics (e.g., Trump, Biden), ensure all news is from {today} only.
                Do not include older articles."""
            else:
                news_prompt = prompt + "\nInclude sources and verify all dates are current."
            
            grok_response = get_grok_response(news_prompt)
            
            verification_prompt = f"""
            Previous response: {grok_response}
            
            Please verify:
            1. All dates match today's date ({today})
            2. All URLs are valid and accessible
            3. Content is current and accurate
            
            If any information is outdated or incorrect, please provide updated information with current sources."""
            
            final_response = get_grok_response(verification_prompt)
            
            st.chat_message("assistant").markdown(final_response)
            st.session_state.conversation.append({"role": "assistant", "content": final_response})

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
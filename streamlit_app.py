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
                "content": f"You are a real-time news assistant. For each headline, include both the date and time published. Always specify if the news is from {today}."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "temperature": 0.2,
        "max_tokens": 500
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

# Title
st.title("AI Assistant")

# Initialize chat history and last news response
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_news" not in st.session_state:
    st.session_state.last_news = None

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Check if this is a follow-up question about news
        if any(word in prompt.lower() for word in ['these headlines', 'this news', 'when was this']):
            if st.session_state.last_news:
                response = anthropic.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1024,
                    system="You are analyzing news headlines. Reference the dates and times in your response.",
                    messages=[{
                        "role": "user",
                        "content": f"Previous headlines: {st.session_state.last_news}\n\nUser question: {prompt}"
                    }]
                )
                assistant_response = response.content[0].text if isinstance(response.content, list) else response.content
                with st.chat_message("assistant"):
                    st.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            else:
                st.error("No recent headlines to reference. Try asking for news headlines first.")

        # Check if this is a news request
        elif any(word in prompt.lower() for word in ['news', 'headlines', 'current events']):
            today = datetime.now().strftime("%Y-%m-%d")
            news_prompt = f"""Provide ONLY today's ({today}) top news headlines. 
            For each headline, include:
            [DATE PUBLISHED] [TIME PUBLISHED] - [HEADLINE] - [ONE-LINE SUMMARY]
            
            Provide exactly what was requested (e.g., if 5 headlines were asked for, provide exactly 5).
            Only include news from {today}. Be explicit about the publishing date and time for each headline."""
            
            grok_response = get_grok_response(news_prompt)
            st.session_state.last_news = grok_response  # Store the news response
            
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
    st.session_state.last_news = None
    st.rerun()
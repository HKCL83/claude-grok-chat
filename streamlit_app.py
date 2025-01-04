import streamlit as st
from anthropic import Anthropic
import requests
import json

# Page config
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize API keys from secrets
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
GROK_API_KEY = st.secrets["GROK_API_KEY"]

# Title and Model Selection
st.title("AI Chat Assistant")
model_choice = st.selectbox("Choose AI Model", ["Claude", "Grok"])

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
        if model_choice == "Claude":
            # Get Claude's response
            response = anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            assistant_response = response.content
            
        else:  # Grok
            # Grok API endpoint
            url = "https://api.x.ai/v1/chat/completions"  # Updated Grok endpoint
            headers = {
                "Authorization": f"Bearer {st.secrets['GROK_API_KEY']}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "grok-1",
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(url, headers=headers, json=data)
            response_data = response.json()
            assistant_response = response_data['choices'][0]['message']['content']

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(assistant_response)
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.experimental_rerun()
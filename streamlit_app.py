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
                messages=[{
                    "role": "system",
                    "content": "You are a helpful AI assistant. Provide direct, concise answers. If you don't have access to real-time data, simply state that clearly and briefly."
                }, {
                    "role": "user",
                    "content": prompt
                }]
            )
            # Extract just the text content from Claude's response
            assistant_response = str(response.content[0].text) if hasattr(response.content[0], 'text') else response.content
            
        else:  # Grok
            st.warning("Grok API access requires credits. Currently unavailable.")
            assistant_response = "Grok API access requires credits. Please try using Claude instead."

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
import streamlit as st
from anthropic import Anthropic
import requests
import json
from datetime import datetime

# Page config and API keys initialization remain the same

def get_claude_response(prompt, system_message="You are a versatile AI assistant."):
    messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.conversation[-5:]] if "conversation" in st.session_state else []
    messages.append({"role": "user", "content": prompt})
    
    response = anthropic.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        system=system_message,
        messages=messages
    )
    
    return response.content[0].text if isinstance(response.content, list) else response.content

def get_grok_response(prompt, system_message="You are a real-time news assistant."):
    # ... (previous implementation for news)
    # Here you might also add logic for image rendering if available
    pass

def get_image(prompt):
    # This function is a placeholder for when you have an actual image generation API from Grok
    return "Image would be generated here if API was available."

# Main App Logic
st.title("AI Assistant")

# Initialize conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Display chat history
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to know?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.conversation.append({"role": "user", "content": prompt})

    try:
        if "latest news" in prompt.lower() or "current events" in prompt.lower():
            news_response = get_grok_response(prompt, "You are a real-time news assistant.")
            st.chat_message("assistant").markdown(news_response)
            st.session_state.conversation.append({"role": "assistant", "content": news_response})
        elif "render image" in prompt.lower() or "generate image" in prompt.lower():
            # Placeholder for image rendering, actual implementation would require API access
            image_response = get_image(prompt)
            st.chat_message("assistant").markdown(f"Image generated: {image_response}")
            st.session_state.conversation.append({"role": "assistant", "content": image_response})
        else:
            claude_response = get_claude_response(prompt)
            st.chat_message("assistant").markdown(claude_response)
            st.session_state.conversation.append({"role": "assistant", "content": claude_response})
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Clear Chat functionality remains the same
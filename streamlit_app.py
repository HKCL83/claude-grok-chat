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

# Title and Feature Selection
st.title("Enhanced AI Assistant")
feature_choice = st.selectbox("Choose Feature", [
    "General Chat", 
    "Current News Analysis", 
    "Image Generation & Analysis",
    "Code Development"
])

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
        if feature_choice in ["Current News Analysis", "Image Generation & Analysis"]:
            # First get Grok's response (when available)
            grok_prompt = f"Regarding: {prompt}\nProvide factual, current information or generate an image as requested."
            """
            # This will be implemented when Grok credits are available
            grok_response = get_grok_response(grok_prompt)
            """
            # Temporary placeholder
            grok_response = "Grok API access requires credits. Currently unavailable."

            # Then have Claude enhance/interpret Grok's response
            claude_prompt = f"""
            Task: {feature_choice}
            User Query: {prompt}
            Raw Information: {grok_response}

            Please provide an enhanced, well-structured response incorporating this information.
            For news, add context and analysis.
            For images, provide detailed descriptions and insights.
            """
        else:
            # Direct Claude interaction for general chat and coding
            claude_prompt = prompt

        # Get Claude's response
        response = anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            system="You are an advanced AI assistant with expertise in analysis, coding, and communication. When given real-time data or images, analyze and explain them thoroughly. For coding, provide detailed, well-documented solutions.",
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
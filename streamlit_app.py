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

def get_grok_response(prompt, system_message="You are a helpful assistant with access to real-time information."):
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
        st.write("Debug - Grok Raw Response:", response.json())  # Debug line
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        if hasattr(response, 'text'):
            error_details = response.json()
            st.error(f"Error details: {error_details}")
        raise Exception(f"Grok API error: {str(e)}\nResponse: {response.text if hasattr(response, 'text') else 'No response'}")

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
            # Prepare Grok prompt based on feature
            if feature_choice == "Current News Analysis":
                grok_system_message = """You are a news assistant with access to real-time information. 
                When asked for news headlines, provide exactly what is requested in a clear, numbered format.
                Include the date and basic details for each headline."""
                
                if "headlines" in prompt.lower():
                    grok_prompt = """Please provide exactly 5 of the most important current news headlines.
                    Format them as:
                    1. [Headline] - [Brief one-line summary] (Date)
                    2. [Headline] - [Brief one-line summary] (Date)
                    etc."""
                else:
                    grok_prompt = f"Please provide detailed current news about: {prompt}. Include dates and key developments."
            else:  # Image Generation & Analysis
                grok_system_message = "You are an image generation assistant. Create and describe images based on prompts."
                grok_prompt = f"Please generate an image based on this description: {prompt}"
            
            # Get Grok's response
            try:
                grok_response = get_grok_response(grok_prompt, grok_system_message)
                st.write("Debug - Grok Response:", grok_response)  # Debug line
            except Exception as e:
                st.error(f"Grok API error: {str(e)}")
                grok_response = "Error fetching data from Grok"

            # Have Claude interpret/enhance Grok's response
            claude_prompt = f"""
            Task: {feature_choice}
            User Query: {prompt}
            Grok's Response: {grok_response}

            Please provide an enhanced analysis:
            - For news: Add context, implications, and detailed analysis
            - For images: Provide detailed description and creative insights
            - Maintain your natural communication style
            - Be direct and informative
            """
        else:
            # Direct Claude interaction for general chat and coding
            claude_prompt = prompt

        # Get Claude's response
        response = anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            system="You are an advanced AI assistant. For news analysis, provide context and implications. For image responses, describe and analyze thoroughly. For coding, provide detailed solutions. Always maintain your natural communication style.",
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
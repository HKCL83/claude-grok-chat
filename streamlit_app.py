import streamlit as st
from anthropic import Anthropic

# Page config
st.set_page_config(
    page_title="Claude Chat",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("AI Chat Assistant")

# Initialize Anthropic client (we'll add proper API key handling next)
anthropic = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

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

    # Get Claude's response
    try:
        response = anthropic.messages.create(
            model="claude-3-opus-20240229",
            messages=st.session_state.messages
        )
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response.content)
        st.session_state.messages.append({"role": "assistant", "content": response.content})
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
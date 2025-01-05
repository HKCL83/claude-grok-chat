import streamlit as st

# Page config
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Title
st.markdown("""
<style>
.title-container {
    text-align: center;
    padding: 50px 0;
    font-size: 24px;
    color: #4a4a4a;
}
.star-icon {
    color: #e65c00;
    font-size: 30px;
}
.button-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
}
.button-container button {
    width: 22%;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #ccc;
    background-color: #e0e0e0;
    color: #007bff;
    font-size: 16px;
}
.custom-text-input {
    display: flex;
    align-items: center;
    background-color: #e0e0e0;
    border-radius: 25px;
    padding: 10px 15px;
    margin: 20px 0;
    width: 100%;
}
.custom-text-input .plus-icon {
    color: #b0b0b0;
    font-size: 20px;
    margin-right: 10px;
    cursor: pointer;
}
.custom-text-input input {
    background: none;
    border: none;
    outline: none;
    width: 100%;
    font-size: 16px;
}
.custom-text-input .mic-icon {
    color: #b0b0b0;
    font-size: 20px;
}
.clear-chat {
    margin-top: 20px;
}
.clear-chat button {
    width: 100%;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #ccc;
    background-color: #e0e0e0;
    color: #007bff;
    font-size: 16px;
}
</style>
<div class="title-container">
    <span class="star-icon">🌟</span><br>
    How can I help you this evening?
</div>
<div class="button-container">
    <button>Camera</button>
    <button>Photos</button>
    <button>Files</button>
    <div class="custom-text-input">
        <span class="plus-icon" onclick="document.getElementById('file_uploader').click()">➕</span>
        <input type="text" placeholder="Ask anything" id="chat_input">
        <span class="mic-icon">🎙️</span>
    </div>
</div>
<div class="clear-chat">
    <button onclick="document.getElementById('clear_chat_button').click()">Clear Chat</button>
</div>
<input type="file" id="file_uploader" style="display:none;" multiple onchange="handleFileUpload(this.files)">
""", unsafe_allow_html=True)

# Chat input with custom styling
prompt = st.text_input("", key="chat_input", placeholder="Ask anything")

# File upload functionality simulation
def handleFileUpload(files):
    for file in files:
        st.session_state.conversation.append({"role": "user", "content": f"User uploaded a file: {file.name}"})
    st.experimental_rerun()

if prompt:
    st.session_state.conversation.append({"role": "user", "content": prompt})
    try:
        # Here you would handle the chat functionality, but since we can't execute code, this is left as a placeholder.
        st.write("AI response would be here")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Display chat history
for message in st.session_state.conversation:
    st.write(f"{message['role'].capitalize()}: {message['content']}")

# Add a clear chat button
if st.button("Clear Chat", key="clear_chat_button"):
    st.session_state.conversation = []
    st.experimental_rerun()
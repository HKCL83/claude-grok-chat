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
</style>
<div class="title-container">
    <span class="star-icon">🌟</span><br>
    How can I help you this evening?
</div>
""", unsafe_allow_html=True)

# Chat input with file upload options
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Camera"):
        st.write("Camera functionality would be implemented here")

with col2:
    if st.button("Photos"):
        uploaded_file = st.file_uploader("Choose a photo", type=["jpg", "jpeg", "png"], key="photo_uploader")
        if uploaded_file is not None:
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
            st.write(f"Photo uploaded: {file_details['FileName']}")
            st.session_state.conversation.append({"role": "user", "content": f"User uploaded a photo: {file_details['FileName']}"})

with col3:
    if st.button("Files"):
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"], key="file_uploader")
        if uploaded_file is not None:
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
            st.write(f"File uploaded: {file_details['FileName']}")
            st.session_state.conversation.append({"role": "user", "content": f"User uploaded a file: {file_details['FileName']}"})

# Custom styled text input
st.markdown("""
<style>
.custom-text-input {
    display: flex;
    align-items: center;
    background-color: #e0e0e0;
    border-radius: 25px;
    padding: 10px 15px;
    margin: 20px 0;
}
.custom-text-input .plus-icon {
    color: #b0b0b0;
    font-size: 20px;
    margin-right: 10px;
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
</style>
""", unsafe_allow_html=True)

# Chat input with custom styling
with st.container():
    st.markdown('<div class="custom-text-input"><span class="plus-icon">➕</span><input type="text" placeholder="Ask anything" id="chat_input"><span class="mic-icon">🎙️</span></div>', unsafe_allow_html=True)
    prompt = st.text_input("", key="chat_input", placeholder="Ask anything")

if prompt:
    st.session_state.conversation.append({"role": "user", "content": prompt})
    try:
        # Here you would handle the chat functionality, but since we can't execute code, this is left as a placeholder.
        # For example:
        # response = get_response(prompt)
        # st.session_state.conversation.append({"role": "assistant", "content": response})
        # st.write(response)
        st.write("AI response would be here")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Display chat history
for message in st.session_state.conversation:
    st.write(f"{message['role'].capitalize()}: {message['content']}")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.conversation = []
    st.experimental_rerun()
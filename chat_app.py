# chat_app.py

import streamlit as st
from wolof_assistant import WolofAssistant

st.set_page_config(page_title="Wolof AI Assistant", page_icon="🟣")
st.title("Wolof AI Assistant")
st.write("Ask questions about Wolof language, grammar, or vocabulary!")

# Initialize assistant once per session
if "assistant" not in st.session_state:
    st.session_state.assistant = WolofAssistant()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Accept user input
user_input = st.chat_input("Type your Wolof question here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    answer = st.session_state.assistant.answer(user_input)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()


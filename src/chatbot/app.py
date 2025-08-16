# src/chatbot/app.py

import streamlit as st
from chatbot.lib.chain import get_chain

# --- Page Configuration ---
st.set_page_config(page_title="RAG Chatbot", layout="centered")
st.title("📄 RAG Chatbot")
st.write("Ask me anything about the documents you uploaded!")

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you today?"}]

# --- Load the RAG Chain ---
chain = get_chain()

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Input ---
if prompt := st.chat_input("Your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and retrieving context..."):
            # The new chain just takes the prompt string directly
            response = chain.invoke(prompt)
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
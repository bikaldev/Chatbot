import streamlit as st
from main import ResponseGenerator, generate_text

# Page Configuration
st.set_page_config(page_title="Chat Interface", layout="wide")


# App Session State for Chat History
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [{
        "role": "ai",
        "content": "How may I help you today?"
    }]
    st.session_state["response"] = ResponseGenerator()
    st.session_state["response_gen"] = st.session_state["response"].generator()
    next(st.session_state["response_gen"])

for message in st.session_state["chat_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("How can I help you?"):
    with st.chat_message("human"):
        st.write(prompt)
    
    st.session_state["chat_history"].append({"role":"human", "content":prompt})
    response = st.session_state["response_gen"].send(prompt)
    next(st.session_state["response_gen"])

    with st.chat_message("ai"):
        st.write_stream(generate_text(response))
    
    st.session_state["chat_history"].append({"role":"ai", "content":response})


uploaded_files = st.file_uploader(
    "Upload documents to chat with.", accept_multiple_files=True, type=['txt', 'pdf','docx']
)
if uploaded_files is not None:
    with st.spinner("Processing files..."):
        for uploaded_file in uploaded_files:
            st.session_state["response"].rag_chat.add_to_vectorstore(uploaded_file)
        uploaded_files = []
    


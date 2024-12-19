import streamlit as st
from config import *

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "context" not in st.session_state:
    st.session_state.context = ""

if "state" not in st.session_state:
    st.session_state.state = ""

# Sidebar components
st.sidebar.markdown(
    '<h1 style="text-align: center; color: darkgrey;">Add Files Below</h1><hr><br>',
    unsafe_allow_html=True,
)
url = st.sidebar.text_input(label="Add URL below:", placeholder="https://www.google.com")
file = st.sidebar.file_uploader(label="Upload PDF below:", type=["pdf"])

# Handle cases based on input
if file is not None and url != "":
    col1, col2 = st.columns([1, 1])
    with col1:
        url_btn = st.button("URL", use_container_width=True)
    with col2:
        pdf_btn = st.button("PDF", use_container_width=True)

    if url_btn:
        st.session_state.messages = []
        st.session_state.context = "url"
        st.session_state.state = "Answering based on the URL only."
    elif pdf_btn:
        st.session_state.messages = []
        st.session_state.context = "pdf"
        st.session_state.state = "Answering based on the PDF only."

elif file is None and url != "":
    col1, col2, col3 = st.columns([0.5, 1, 0.5])
    with col2:
        url_btn = st.button("URL", use_container_width=True)

    if url_btn:
        st.session_state.messages = []
        st.session_state.context = "url"
        st.session_state.state = "Answering based on the URL only."

elif file is not None and url == "":
    col1, col2, col3 = st.columns([0.5, 1, 0.5])
    with col2:
        pdf_btn = st.button("PDF", use_container_width=True)

    if pdf_btn:
        st.session_state.messages = []
        st.session_state.context = "pdf"
        st.session_state.state = "Answering based on the PDF only."

else:
    st.session_state.state = ""
    st.markdown(
        '<h3 style="text-align:center">Welcome to Robin-AI</h3>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<h6 style="text-align:center;color:grey">Crafted with care, designed to share.</h6>',
        unsafe_allow_html=True,
    )
    
# Display state (if any)
if st.session_state.state:
    st.markdown(
        f'<h6 style="text-align:center;color:lightgrey;">{st.session_state.state}</h6>',
        unsafe_allow_html=True,
    )

st.markdown("<hr>", unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(name=message["role"]):
        st.markdown(message["content"])

# Handle user input
prompt = st.chat_input(placeholder="Ask me here...")
if prompt:
    with st.chat_message(name="user"):
        st.write(prompt)

    # Determine the context and generate a system prompt
    if st.session_state.context == "pdf":
        context = find_context_question(prompt, build_db_from_pdf(file))
        system_prompt = context_prompt.invoke({"context": context}).text
    elif st.session_state.context == "url":
        context = find_context_question(prompt, build_db_from_url(url))
        system_prompt = context_prompt.invoke({"context": context}).text
    else:
        system_prompt = general_prompt.invoke({}).text

    # Build the response
    message = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt),
    ]
    response = llm_model.invoke(message).content

    # Display AI response
    with st.chat_message(name="ai"):
        st.write(response)

    # Append messages to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "ai", "content": response})

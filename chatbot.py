import streamlit as st
from streamlit_chat import message
import os
from dotenv import load_dotenv
import openai

from tools.login_checker import LoginChecker


def update_chat(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages


load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

st.title("RedTeamAGPT")

tools = ["Social Engineering", "Vulnerability", "Password cracking", "Anomaly Detection", "LLM hallucinations", "Behaviour Analysis", "Network Segmentation", "Finding Zero Day", "DDoS"]
model = st.selectbox("Select a tool", options=tools)


if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = []


query = st.text_input("Query: ", key="input")


if query:
    with st.spinner("generating..."):
        messages = st.session_state['messages']
        messages = update_chat(messages, "user", query)

        lgcheck = LoginChecker(query)
        lgcheck.run()

        # messages = update_chat(messages, "assistant", response)
        # st.session_state.past.append(query)
        # st.session_state.generated.append(response)

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))

    with st.expander("Show Messages"):
        st.write(messages)

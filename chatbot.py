import streamlit as st
from streamlit_chat import message
import os
from dotenv import load_dotenv
import openai
import validators

from tools.login_checker import LoginChecker


def update_chat(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages


load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

st.title("RedTeamAGPT")

tools = ["Login Checker"]
model = st.selectbox("Select a tool", options=tools)


if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = []


if "Login Checker" == model:
    while True:
        messages = update_chat(messages, "user", "Enter in the url")
        http_url =  st.text_input("", key="input")
        if validators.url(http_url):
            break
        else:
            error_resp = f"{http_url} is not a valid URL. Try again"
            update_chat(messages, "assistant", error_resp)
            st.session_state.past.append(model)
            st.session_state.generated.append(error_resp)

    with st.spinner("Testing website {http_url}. This will take a while."):
        messages = st.session_state['messages']
        lgcheck = LoginChecker(http_url)
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

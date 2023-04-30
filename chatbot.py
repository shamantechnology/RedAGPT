import streamlit as st
from streamlit_chat import message
import os
from dotenv import load_dotenv
import openai
import validators
import multiprocessing
import time
from datetime import datetime

from tools.login_checker import LoginChecker

def run_login_checker(http_url, logfile):
    lgcheck = LoginChecker(http_url, logfile)
    lgcheck.run()    

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
        
        log_file_path = f"{os.path.abspath('tools/logs/')}/runlog{datetime.now().strftime('%Y%m%d_%H%M')}.txt"

        process = multiprocessing.Process(target=run_login_checker, args=(http_url,log_file_path,))

        process.start()
        process.join()

        seek_pos = None
        while process.is_alive:
            if os.path.exists(log_file_path):
                with open(log_file_path, "r") as runtxt:
                    if seek_pos:
                        runtxt.seek(seek_pos)

                    if len(runtxt.readlines) > 0:
                        log_response = runtxt.readlines()
                        messages = update_chat(messages, "assistant", log_response)
                        st.session_state.past.append(model)
                        st.session_state.generated.append(log_response)

                    seek_pos = runtxt.tell()
                    time.sleep(10)

            process.join()
            if process.exitcode is not None:
                break

        # messages = update_chat(messages, "assistant", response)
        # st.session_state.past.append(query)
        # st.session_state.generated.append(response)

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))

    with st.expander("Show Messages"):
        st.write(messages)

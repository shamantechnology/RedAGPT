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


if 'messages' not in st.session_state:
    st.session_state['messages'] = []

## First msgs
# if 'generated' not in st.session_state:
#     st.session_state['generated'] = [update_chat([], "user", "okay")]

# if 'past' not in st.session_state:
#     st.session_state['past'] = [update_chat([], "assistant", "Enter in the url")]

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'allow_url_to_be_checked' not in st.session_state:
    st.session_state['allow_url_to_be_checked'] = False

if 'url_checked' not in st.session_state:
    st.session_state['url_checked'] = False

if 'first_chatbot_msg' not in st.session_state:
    st.session_state['first_chatbot_msg'] = True

if 'seek_pos' not in st.session_state:
    st.session_state['seek_pos'] = None

if 'process_started' not in st.session_state:
    st.session_state['process_started'] = False


## Try to show the first msg in the bot 

# if st.session_state['first_chatbot_msg']:
#     for i in range(len(st.session_state['generated'])-1, -1, -1):
#         message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
#         message(st.session_state["generated"][i], key=str(i))

#     with st.expander("Show Messages"):
#         st.write(st.session_state['generated'])

#     st.session_state['first_chatbot_msg'] = False

tools = ["Login Checker"]
model = st.selectbox("Select a tool", options=tools)

if model == "Login Checker":
    messages = st.session_state['messages']

    messages = update_chat(messages, "user", "Enter in the url")
    # http_url = st.text_input("", key="input_http")
    http_url = st.text_input("", placeholder="Enter the URL here", key="input_http")

    if not st.session_state['allow_url_to_be_checked']:
        if validators.url(http_url):
            st.session_state['allow_url_to_be_checked'] = True

    if st.session_state['allow_url_to_be_checked'] and st.session_state['url_checked'] == False:
        with st.spinner(f"Testing website {http_url}. This will take a while."):
            messages = st.session_state['messages']
            
            log_file_path = f"{os.path.abspath('tools/logs/')}/runlog{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            process = multiprocessing.Process(target=run_login_checker, args=(http_url,log_file_path,))

            process.start()
            process.join()

            if not st.session_state['process_started']:
                process = multiprocessing.Process(target=run_login_checker, args=(http_url, log_file_path,))
                process.start()
                st.session_state['process_started'] = True

            if os.path.exists(log_file_path):
                with open(log_file_path, "r") as runtxt:
                    if st.session_state['seek_pos']:
                        runtxt.seek(st.session_state['seek_pos'])

                    lines = runtxt.readlines()
                    if len(lines) > 0:
                        log_response = lines
                        messages = update_chat(messages, "assistant", log_response)
                        st.session_state.past.append(model)
                        st.session_state.generated.append(log_response)

                    st.session_state['seek_pos'] = runtxt.tell()

            if not process.is_alive():
                st.success("Login Checker process has completed.")
                st.session_state['process_started'] = False
            else:
                st.experimental_rerun()


            st.session_state['url_checked'] = True
            

## Show msgs in the bot

# if st.session_state['generated']:

#     for i in range(len(st.session_state['generated'])-1, -1, -1):
#         message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
#         message(st.session_state["generated"][i], key=str(i))

#     with st.expander("Show Messages"):
#         st.write(messages)

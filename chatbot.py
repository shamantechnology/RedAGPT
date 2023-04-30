import streamlit as st
from streamlit_chat import message
import os
from dotenv import load_dotenv
import openai
import validators
import multiprocessing
from datetime import datetime
import base64

from tools.login_checker import LoginChecker

def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        img_bytes = f.read()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url('data:image/png;base64,{base64.b64encode(img_bytes).decode()}');
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def run_login_checker(http_url, logfile):
    lgcheck = LoginChecker(http_url, logfile)
    lgcheck.run()    

def update_chat(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages

# Add img to the bg
bg_img_path = os.path.abspath("bg_img.jpg")
add_bg_from_local(bg_img_path)


load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

st.markdown('<h1 style="color: white;">RedTeamAGPT</h1>', unsafe_allow_html=True)

if "show_first_chatbot_msg" not in st.session_state:
    st.session_state['show_first_chatbot_msg'] = True

if "show_url_msg_once" not in st.session_state:
    st.session_state['show_url_msg_once'] = True

if 'set_local_or_remote' not in st.session_state:
    st.session_state['set_local_or_remote'] = False

if 'user_local_remote' not in st.session_state:
    st.session_state['user_local_remote'] = None

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# First msgs in the bot
if 'generated' not in st.session_state:
    st.session_state['generated'] = ["Local OR Remote"]
if 'past' not in st.session_state:
    st.session_state['past'] = [""]

if 'allow_url_to_be_checked' not in st.session_state:
    st.session_state['allow_url_to_be_checked'] = False

if 'url_checked' not in st.session_state:
    st.session_state['url_checked'] = False

if 'seek_pos' not in st.session_state:
    st.session_state['seek_pos'] = None

if 'process_started' not in st.session_state:
    st.session_state['process_started'] = False


tools = ["Login Checker"]
model = st.selectbox("Tools", options=tools)

if model == "Login Checker":
    if not st.session_state['set_local_or_remote']:
        placeholder = "Local or Remote"
    else:
        placeholder = "Enter URL here"

    input_text = st.text_input("", placeholder=placeholder, key="input_text", label_visibility='hidden')
    st.session_state['past'].append(input_text)


    if not st.session_state['set_local_or_remote']:

        if input_text == "Local" or input_text == "Remote":
            st.session_state["user_local_remote"] = input_text # save the user's input
            st.session_state['set_local_or_remote'] = True
            st.experimental_rerun() # Rerun the script so the "Enter URL here" can be shown in the box
        else:
            if not st.session_state['show_first_chatbot_msg']: # show this msg in the bot only if it's not the first msg of the bot
                st.session_state['generated'].append("Give Local or Remote")

    if st.session_state['set_local_or_remote']:

        #################### this part: still not shows the msg before u give the url but afterwards but that's ok #######
        # The bot should ask the user to give a url or ip based on their previous option
        if st.session_state["show_url_msg_once"]:
            if st.session_state["user_local_remote"] == "Local":
                msg = "GIVE URL"
            else: # Remote
                msg = "REMOTE SHOULD ONLY BE DONE ON IPs YOU OWN"
            
            st.session_state['generated'].append(msg)
            message(msg, key=str(len(st.session_state['generated'])))

            st.session_state["show_url_msg_once"] = False
            st.experimental_rerun() # Rerun script to show the url msg in the bot
        ###################################################################################################################
        
        if not st.session_state['allow_url_to_be_checked'] and len(input_text) != 0:
            if validators.url(input_text):
                st.session_state['allow_url_to_be_checked'] = True
            else:
                st.session_state['generated'].append("The given URL is invalid")

        if st.session_state['allow_url_to_be_checked'] and not st.session_state['url_checked']:
            with st.spinner(f"Testing website {input_text}. This will take a while."):
                
                log_file_path = f"{os.path.abspath('tools/logs/')}/runlog{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                if not os.path.exists(log_file_path):
                    open(log_file_path, 'w').close()

                if not st.session_state['process_started']:
                    process = multiprocessing.Process(target=run_login_checker, args=(input_text, log_file_path,))
                    process.start()
                    process.join()
                    st.session_state['process_started'] = True

                if os.path.exists(log_file_path):
                    with open(log_file_path, "r") as runtxt:
                        if st.session_state['seek_pos']:
                            runtxt.seek(st.session_state['seek_pos'])

                        lines = runtxt.readlines()
                        if len(lines) > 0:
                            log_response = lines
                            st.session_state.past.append(model)
                            st.session_state.generated.append(log_response)

                        st.session_state['seek_pos'] = runtxt.tell()

                process.join()
                if not process.is_alive():
                    st.success("Login Checker process has completed.")
                    st.session_state['process_started'] = False
                else:
                    st.experimental_rerun()


                st.session_state['url_checked'] = True


## Show the first msg in the chatbot
if st.session_state['show_first_chatbot_msg']:
    message(st.session_state["generated"], key=str(0))
    st.session_state['show_first_chatbot_msg'] = False


## Show msgs in the bot
## if the two lists do not match, then won't be shown
filtered_past = [(i, msg) for i, msg in enumerate(st.session_state['past']) if len(msg) != 0]
filtered_generated = [(i, msg) for i, msg in enumerate(st.session_state['generated']) if len(msg) != 0]

for (past_i, past_msg), (generated_i, generated_msg) in reversed(list(zip(filtered_past, filtered_generated))):
    message(past_msg, is_user=True, key=str(past_i) + '_user')
    message(generated_msg, key=str(generated_i))

    # with st.expander("Show Messages"):
    #     st.write(messages)

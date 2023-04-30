"""
Using langchains create a task to check the security
of a login form found at a specific web address

THIS IS DANGEROUS TO RUN

Uses the hydra cli program
https://www.cyberpunk.rs/password-cracker-thc-hydra
"""
import os
import uuid
import sys
import random

from langchain.agents import Tool
from langchain.utilities import BashProcess
from langchain.tools.file_management.write import WriteFileTool
from langchain.tools.file_management.read import ReadFileTool
from langchain.tools.python.tool import PythonREPLTool
from langchain.utilities import GoogleSearchAPIWrapper

from langchain.vectorstores.redis import Redis
import redis
from langchain.embeddings import OpenAIEmbeddings

from langchain.experimental import AutoGPT
from langchain.chat_models import ChatOpenAI

from urllib.parse import urlparse
from datetime import datetime
import logging

# setup global logging

# Configure the logging module to write the output to a file
logging.basicConfig(
    filename=f'{os.path.abspath("tools/logs/")}/runlog{datetime.now().strftime("%Y%m%d_%H%M")}.txt', level=logging.INFO)

def logging_run(output):
        """
        for log to file during a run
        """
        logging.info(output)


class LoginChecker:
    def __init__(self, http_url):
        # prompt for the agent to use, will be a list
        data_path = os.path.abspath("tools/data/")
        logs_path = os.path.abspath("tools/logs/")
        bin_path = os.path.abspath("tools/bin")

        self.http_url = http_url

        self.logging_file = f"{logs_path}/runlog{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        self.logging = logging.basicConfig(filename=self.logging_file, level=logging.INFO)

        self.pid = uuid.uuid4()
        
        self.tools = [
            Tool(
                "search",
                GoogleSearchAPIWrapper().run,
                """
                Useful for when you need to answer questions about current events. 
                You should ask targeted questions
                """
            ),
            PythonREPLTool(),
            Tool(
                "bash",
                BashProcess().run,
                "useful for when you want to run a command in the bash terminal."
            ),
            WriteFileTool(),
            ReadFileTool()
        ]
        
        self.embeddings = OpenAIEmbeddings()

        error_log = f"{logs_path}/error{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        info_log =  f"{logs_path}/info{datetime.now().strftime('%Y%m%d_%H%M')}.txt"

        urlparts = urlparse(self.http_url)
        hostport = urlparts.netloc.split(":")
        if len(hostport) == 2:
            hydra_host = f"-s {hostport[1]} {hostport[0]}"
        else:
            hydra_host = f"{hostport[0]}"

        self.goals = [
            f"Check if log files {info_log} and {error_log} exist and if not, create them"
            f"""
            In bash run the command 'hydra -v -L {data_path + "/username_list_small.txt"} -P {data_path + "/password_list_small.txt"} {hydra_host} http-post-form -o /home/host/Project/Python/RedAGPT/RedAGPT/tools/logs/hydra_log.txt '/admin/login/:username=^USER^&password=^PASS^:F=Invalid username or password'" > {info_log} 2> {error_log}'. Only use bash and not python
            """,
            # "Understand what the selenium python library is",
            # f"Read the source of the website {self.http_url} using curl",
            # f"""
            # Use the "write_file" command. Using the source of {self.http_url}, write a python program using selenium python and its WebDriver API at {bin_path} with name login_test.py. The program has to iterate through the username list {data_path + "/username_list_small.txt"} with every password at {data_path + "/password_list_small.txt"} and try to login at {self.http_url}. Store the python program at {bin_path}. Place all stdout to {info_log}. Place all stderr to {error_log}.
            # """,
            f"""
            Keep logs and the final security report at {logs_path + '/'}. Create a summary security report using the {info_log} and {error_log} logs. Include a summery at the end of the report detailing if anything found wrong and how to fix issues.
            """
        ]

        try:
            # check if index name exists and if not create it
            # connect to Redis server
            redis_check = redis.Redis.from_url(os.environ["REDIS_URL"])
            redis_idx_name = f'{os.environ["REDIS_INDEX_NAME"]}_{self.pid}'

            # check if the index exists
            if len(redis_check.keys(
                "doc:{}*".format(redis_idx_name)
            )) == 0:
                # create the index if it doesn't exist
                Redis.from_texts(
                    texts=["hacker"],
                    redis_url=os.environ["REDIS_URL"],
                    index_name=redis_idx_name,
                    embedding=self.embeddings
                )

            self.vectorstore = Redis(
                redis_url=os.environ["REDIS_URL"],
                index_name=redis_idx_name,
                embedding_function=self.embeddings.embed_query
            )

        except Exception as err:
            print("Redis creation failed {err}")
            # yield err
            raise err
        
    
    def run(self):
        ai_names = ["Kevin", "Neo", "Trinity", "JC Denton", "Hiro Protagonist", "Acid Burn", "System Override", "MrMr", "Django", "Superman"]
        ai_roles = ["White Hat Hacker", "Cybersecurity Expert", "IT Admin", "Leet Hacker", "Scriptkiddie", "Programmer"]

        ai_name = random.choice(ai_names)
        ai_role = random.choice(ai_roles)

        print(f"\n Name {ai_name} \n Role {ai_role}\n")
        agent = AutoGPT.from_llm_and_tools(
            ai_name=ai_name,
            ai_role=ai_role,
            tools=self.tools,
            llm=ChatOpenAI(temperature=1),
            memory=self.vectorstore.as_retriever()
        )

        # Set verbose to be true
        agent.chain.verbose = False

        # give prompt for running login test
        # closed for now but will need a list of different ones to choose
        sys.stdout.write = logging_run
        astr = agent.run(self.goals)
        print(f"astr {astr}\n")

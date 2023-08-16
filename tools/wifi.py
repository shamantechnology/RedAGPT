"""
WIFI Class

Creates an autonomous agent that uses aircrack-ng to analyze local
WIFI security up to WIFI adapter's max range

Creates a report on what can be done to secure these networks.

THIS IS DANGEROUS TO RUN

aircrack-ng
https://github.com/aircrack-ng/aircrack-ng

langchain
https://github.com/langchain-ai/langchain
"""

import uuid
import os
from datetime import datetime
import logging
import sys

from tools.stream_to_logger import StreamToLogger

##########################
# langchain import block #
##########################
from langchain.agents import Tool
from langchain.utilities import BashProcess
from langchain.tools.file_management.write import WriteFileTool
from langchain.tools.file_management.read import ReadFileTool
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.tools import DuckDuckGoSearchRun
from langchain.vectorstores.redis import Redis
from langchain.embeddings import OpenAIEmbeddings
from langchain.experimental import AutoGPT
from langchain.chat_models import ChatOpenAI

class WIFI:
    def __init__(self):
        # unique name of the agent used for redis vector store
        self.uuid = str(uuid.uuid4()).replace('-', '')

        # logging and security report setup
        logs_path = os.path.abspath("tools/logs/")
        self.logging_file_name = f"wifi_runlog{datetime.now().strftime('%Y%m%d_%H%M')}_{self.uuid}.txt"
        self.logging_file_path =  f"{logs_path}/{self.logging_file_name}"
        self.summary_file_name = f"wifi_security_report{datetime.now().strftime('%Y%m%d_%H%M')}_{self.uuid}.txt"
        self.summary_file_path = f"{logs_path}/{self.summary_file_name}"

        if not os.path.exists(logs_path):
            os.makedirs(logs_path)

        if not os.path.exists(self.logging_file_path):
            open(self.logging_file_path, "w").close()
        
        logging.basicConfig(
            filename=self.logging_file_path,
            level=logging.INFO,
            format="\n%(message)s\n")

        self.logging = logging.getLogger(__name__)

        try:
            # setup logging of the stdout of the console agent is ran in
            # this was because the langchain bot run function is a blocking
            # operation
            sys.stdout = StreamToLogger(self.logging, logging.INFO)
        except Exception as err:
            self.logging.error(f"StreamToLogger error: {err}")
            raise err


        # setup langchain tools
        self.tools = [
            Tool(
                "search",
                GoogleSearchAPIWrapper().run,
                """
                Useful for when you need to answer questions about current events. 
                You should ask targeted questions
                """
            ),
            # PythonREPLTool(),
            # ShellTool(),
            Tool(
                "bash",
                BashProcess().run,
                "useful for when you want to run a command in the bash terminal."
            ),
            WriteFileTool(),
            ReadFileTool(),
            Tool(
                "search2",
                DuckDuckGoSearchRun().run,
                """
                Useful for when you need to answer questions about current events. 
                You should ask targeted questions
                Use this when search hits a quota limit
                """

            )
        ]

        # setup text embeddings
        self.embeddings = OpenAIEmbeddings()

        # set goals
        self.goals = [
            """
                Check if the device you are running on has a wifi adapter by running the command 
                    \"\"\"sudo lshw | grep -e wireless -e Wireless\"\"\"
                Reading the output from the command. 
                If there is no output from the command, there is no wifi, end program with message \"Wifi Adapter Needed\".
            """,
            """
                Find the interface name of the wifi using the command ifconfig
            """,
            """
                Run the command airodump-ng followed by the found interface name. For example \"airodump-ng wlan0\"
            """,
            """
                Using the \"ENC\", \"CIPHE\", \"AUTH\", \"ESSID\" fields from the airodump-ng output, 
                    find 5 common security issues that you think would be the most interesting to security analysts 
            """
            f"""
                Create a document at {self.summary_file_path} with the security report of the found local wifi networks and what to do to improve security 
            """
        ]

        # setup vectorstore and run agent
        try:
            # have to manually create an entry first 
            # to make a new index on redis that can be used
            # for vector storage

            Redis.from_texts(
                texts=["hacker"],
                redis_url=os.environ["REDIS_URL"],
                index_name=self.uuid,
                embedding=self.embeddings
            )

            # create vector storage
            self.vectorstore = Redis(
                redis_url=os.environ["REDIS_URL"],
                index_name=self.uuid,
                embedding_function=self.embeddings.embed_query
            )

        except Exception as err:
            print("Redis vectorstore creation error: {err}")
            raise err

    def run(self):
        llm = ChatOpenAI(temperature=0.5, streaming=True)

        agent = AutoGPT.from_llm_and_tools(
            ai_name=self.uuid,
            ai_role="Penetration Tester",
            tools=self.tools,
            llm=llm,
            memory=self.vectorstore.as_retriever()
        )
        agent.chain.verbose = False

        try:
            self.autogpt_resp = agent.run(self.goals)
        except Exception as err:
            print(f"AutoGPT failure {err}")

        if self.autogpt_resp:
            self.logging.info(f"AutoGPT Response: {self.autogpt_resp}")


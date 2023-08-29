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
from langchain_experimental.autonomous_agents import AutoGPT
from langchain.chat_models import ChatOpenAI

class WIFI:
    def __init__(self):
        # unique name of the agent used for redis vector store
        self.uuid = str(uuid.uuid4()).replace('-', '')

        # setup data path
        self.data_path = os.path.abspath("tools/data/")
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)

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
            f"""
             STEP 1
                Check if the device you are running on has a wifi adapter on interface \"{os.environ["USE_WIFI_INTERFACE"]}\" by running the command 
                    \"\"\"sudo ifconfig | grep {os.environ["USE_WIFI_INTERFACE"]}\"\"\"
                Reading the output from the command. 
                If there is no output from the command, there is no wifi, end program with message \"Wifi Adapter Needed\".
            """,
            f"""
            STEP 2
                Set the device wifi to monitor mode by running the command
                    \"\"\"sudo airmon-ng start {os.environ["USE_WIFI_INTERFACE"]}\"\"\"
                If there is an error, end program with message \"Setting up wifi monitoring failed. Please check wifi interface\"
            """,
            f"""
            STEP 3
                Check if the device you are running on has a wifi adapter set to monitor mode with the command 
                    \"\"\"sudo airmon-ng | grep {os.environ["USE_WIFI_INTERFACE"]}mon\"\"\"
                Reading the output from the command. 
                If there is no output from the command, there is no wifi monitoring, end program with message \"Wifi Adapter Set to Monitoring Mode Needed\".
            """,
            f"""
            STEP 4
                Run the command
                \"\"\"sudo timeout 30 airodump-ng -K 1 --manufacturer --uptime --wps --cswitch 1 -w {self.data_path + "/ragpt"} --output-format csv {os.environ["USE_WIFI_INTERFACE"]}mon &\"\"\"
            """,
            """
            STEP 5
                Wait 30 seconds while the command from STEP 4 finishes
            """,
            f"""
            STEP 6
                Read the CSV file {self.data_path + "/ragpt-01.csv"} and using the \"ENC\", \"CIPHER\", \"AUTH\", \"ESSID\", \"UPTIME\" and \"MANUFACTURER\" fields, 
                    find 5 common security issues that would be the most useful and actionable to an IT cybersecurity team  
            """,
            f"""
            STEP 7
                Create a document at {self.summary_file_path} with the security report of the found local wifi networks and what to do to improve security 
            """,
            f"""
            STEP 8
                Delete file {self.data_path + "/ragpt-01.csv"} if present. 
            """,
            f"""
            STEP 9
                End program run with message "WIFI Security Report Completed"
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
                embedding=self.embeddings,
                index_name=self.uuid
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


"""
Using langchains create a task to check the security
of a login form found at a specific web address

THIS IS DANGEROUS TO RUN

Uses the hydra cli program
https://www.cyberpunk.rs/password-cracker-thc-hydra
"""
import os
# import string
# import random

from langchain.agents import Tool
from langchain.utilities import BashProcess
from langchain.tools.file_management.write import WriteFileTool
from langchain.tools.file_management.read import ReadFileTool
from langchain.tools.python.tool import PythonREPLTool
# from langchain.tools.interaction.tool import StdInInquireTool
from langchain.utilities import GoogleSearchAPIWrapper

# from langchain.vectorstores import FAISS
# import faiss
from langchain.docstore import InMemoryDocstore
from langchain.vectorstores.redis import Redis
from langchain.embeddings import OpenAIEmbeddings

from langchain.experimental import AutoGPT
from langchain.chat_models import ChatOpenAI

from langchain.document_loaders import YoutubeLoader


class LoginChecker:
    def __init__(self, http_url):
        self.http_url = http_url
        
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
            # StdInInquireTool(),
            Tool(
                "bash",
                BashProcess().run,
                "useful for when you want to run a command in the bash terminal."
            ),
            WriteFileTool(),
            ReadFileTool()
        ]
        
        self.embeddings = OpenAIEmbeddings()

        # prompt for the agent to use, will be a list
        data_path = os.path.abspath("tools/data/")
        logs_path = os.path.abspath("tools/logs/")
        bin_path = os.path.abspath("tools/bin")
        transcript_path = os.path.abspath("tools/transcripts")
        self.goals = [
            f"""
            You are to use Hydra, a parallelized login cracker, 
            using the local bash terminal to determine the security of a form located at {http_url}: 
              - Hydra is located at /usr/bin/hydra
              - There is a "password_list.txt" at {data_path} and if the file is not found, 
                download using wget a password lists from 
                https://github.com/kkrypt0nn/wordlists/tree/main/passwords 
                and save them to {data_path}. If you receive a 404, use another list.
              - There is a "username_list.txt" at {data_path} abd if the file is not found, 
                download using wget a username lists from 
                https://github.com/kkrypt0nn/wordlists/blob/main/usernames/default_users_for_services.txt 
                and save them to {data_path}. If you receive a 404, use another list.
              - Download all program install files needed to {data_path}
              - Install all program binaries needed to {bin_path}
            """,
            f"""
            Find other security issues not covered by the tools in step 1 with login form at {self.http_url}
                - Install needed security tools
            """,
            """
            Create a natural English language security report for those who 
            are not technically savy to read. Include details of methods used and results found
            - Include a summery at the end of the report detailing what was wrong and how to fix issues.
            - If there are no issues found, return \"No Security Issues Reported\"
            """,
            f"Keep logs and the final security report at {logs_path}"
        ]

        try:
            # loading transcript about hydra as first document
            transcript_path = "{}/CertBrosHowToHydra.txt".format(os.path.abspath("tools/transcripts"))
            with open(transcript_path, "r") as transfile:
                transcript_hydra = transfile.read().replace("\n", "")
                Redis.from_texts(
                    texts=[transcript_hydra],
                    redis_url=os.environ["REDIS_URL"],
                    index_name=os.environ["REDIS_INDEX_NAME"],
                    embedding=self.embeddings
                )

            self.vectorstore = Redis(
                redis_url=os.environ["REDIS_URL"],
                index_name=os.environ["REDIS_INDEX_NAME"],
                embedding_function=self.embeddings.embed_query
            )

            # using faiss
            # possibly can use redis but will need to update
            # the landchain agent.py in experimental for autogpt
            # to use add_text
            # embedding_size = 1536
            # index = faiss.IndexFlatL2(embedding_size)
            # self.vectorstore = FAISS(self.embeddings.embed_query, index, InMemoryDocstore({}), {})

        except Exception as err:
            print("Redis creation failed {err}")
            # yield err
            raise err

    def run(self):
        agent = AutoGPT.from_llm_and_tools(
            ai_name="Kevin",
            ai_role="White Hat Hacker",
            tools=self.tools,
            llm=ChatOpenAI(temperature=0.8),
            memory=self.vectorstore.as_retriever()
        )

        # Set verbose to be true
        agent.chain.verbose = True

        # give prompt for running login test
        # closed for now but will need a list of different ones to choose
        agent.run(self.goals)
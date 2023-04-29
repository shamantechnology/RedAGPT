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
import redis
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

        self.goals = [
            f"""
            You are to use Hydra, a parallelized login cracker, 
            using the local bash terminal to determine the security of a form located at {http_url}: 
              - Use the hydra command `hydra -L {data_path + "/username_list.txt"} -P {data_path + "/password_list.txt"} 127.0.0.1 http-post-form -o {logs_path + "/hydra_log.txt"}
            """,
            f"""
            Using selenium python package and its WebDriver API, create a python program that iterates through the username list {data_path + "/username_list.txt"} with every password  at {data_path + "/password_list.txt"} and try to login at {http_url} and store the python program at {bin_path}
            """,
            """
            Create a natural English language security report for those who 
            are not technically savy to read. Include details of methods used and results found
            - Include a summery at the end of the report detailing what was wrong and how to fix issues.
            - If there are no issues found, return \"No Security Issues Reported\"
            """,
            f"Keep logs and the final security report at {logs_path + '/'}"
        ]

        try:
            # check if index name exists and if not create it
            # connect to Redis server
            redis_check = redis.Redis.from_url(os.environ["REDIS_URL"])

            # check if the index exists
            if not redis_check.exists(os.environ["REDIS_INDEX_NAME"]):
                # create the index if it doesn't exist
                Redis.from_texts(
                    texts=["first"],
                    redis_url=os.environ["REDIS_URL"],
                    index_name=os.environ["REDIS_INDEX_NAME"],
                    embedding=self.embeddings
                )
            else:
                # clear and reset if it does
                redis_check.flushall()
                Redis.from_texts(
                    texts=["first"],
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

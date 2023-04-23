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

from langchain.vectorstores import FAISS
import faiss
from langchain.docstore import InMemoryDocstore
# from langchain.vectorstores.redis import Redis
from langchain.embeddings import OpenAIEmbeddings

from langchain.experimental import AutoGPT
from langchain.chat_models import ChatOpenAI


class LoginChecker:
    def __init__(self, http_url):
        self.http_url = http_url
        
        self.tools = [
            Tool(
                "search",
                GoogleSearchAPIWrapper().run,
                "useful for when you need to answer questions about current events. You should ask targeted questions"),
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
        self.prompt = f"Create a security report for a login form via GET at {self.http_url} using the tool hydra via the bash terminal. Use one or more wordlists from the local folder {data_path}"

        try:
            # embedding size 1536
            # have to manually create index but will need to explore
            # how to create without any text using from_document or from_text

            # going to try a hack of creating a random string of length from
            # langchain example docs for the faiss
            # rand_str_length = 1536
            # rand_str = ''.join(
            #     random.choices(
            #         string.ascii_uppercase + string.digits, k=rand_str_length))
            
            # self.vectorstore = Redis.from_texts(
            #     texts=[rand_str],
            #     redis_url=os.environ["REDIS_URL"],
            #     index_name=os.environ["REDIS_INDEX_NAME"],
            #     embedding=self.embeddings
            # )
            # self.vectorstore = Redis(
            #     redis_url=os.environ["REDIS_URL"],
            #     index_name=os.environ["REDIS_INDEX_NAME"],
            #     embedding_function=self.embeddings.embed_query
            # )

            # using faiss
            embedding_size = 1536
            index = faiss.IndexFlatL2(embedding_size)
            self.vectorstore = FAISS(self.embeddings.embed_query, index, InMemoryDocstore({}), {})
        except Exception as err:
            print("Redis connection failed {err}")
            # yield err
            raise err

    def run(self):
        agent = AutoGPT.from_llm_and_tools(
            ai_name="Kevin",
            ai_role="IT Security",
            tools=self.tools,
            llm=ChatOpenAI(temperature=0),
            memory=self.vectorstore.as_retriever()
        )

        # Set verbose to be true
        agent.chain.verbose = True

        # give prompt for running login test
        # closed for now but will need a list of different ones to choose
        agent.run([self.prompt])

"""
Using langchains create a task to check the security
of a login form found at a specific web address

THIS IS DANGEROUS TO RUN

Uses the hydra cli program
https://www.cyberpunk.rs/password-cracker-thc-hydra
"""
import os
from langchain.agents import Tool
from langchain.utilities import BashProcess



class LoginChecker:
    def __init__(self):
        self.openapi_key = os.environ["OPEN_AI_API"]
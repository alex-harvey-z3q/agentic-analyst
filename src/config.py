import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
MODEL_NAME = "gpt-4.1-mini"  # The default LLM to use for answering questions; change here to switch models.

client = OpenAI(api_key=OPENAI_API_KEY)

from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain.agents import Tool, tool, AgentType, initialize_agent
import os

groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="llama-3.1-8b-instant",
    temperature=0.2,
    # max_tokens=1000,
    # top_p=0.95,
    # frequency_penalty=0,
    # presence_penalty=0,
)


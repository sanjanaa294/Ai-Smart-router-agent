"""
mcp_adapter.py
--------------
Adapter module that interfaces directly with the existing MCP server & LangGraph client in TASK2.
Reuses the FastMCP server tools and LangGraph React Agent without creating mock functions.
"""

import os
import sys
import asyncio
import warnings
import logging
from dotenv import load_dotenv

# Suppress verbose schema warning messages from langchain_google_genai / google SDK
warnings.filterwarnings("ignore")
logging.getLogger("langchain_google_genai").setLevel(logging.ERROR)
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("mcp").setLevel(logging.ERROR)

# Path resolution to TASK2/langgraph_client directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK2_CLIENT_DIR = os.path.join(BASE_DIR, "TASK2", "langgraph_client")

if TASK2_CLIENT_DIR not in sys.path:
    sys.path.insert(0, TASK2_CLIENT_DIR)

load_dotenv(os.path.join(BASE_DIR, "TASK2", ".env"))

from graph import build_graph

_agent_instance = None


async def _get_mcp_agent():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = await build_graph()
    return _agent_instance


async def execute_mcp_async(question: str) -> str:
    """
    Asynchronously invokes the TASK2 LangGraph agent connected to FastMCP server tools.
    """
    agent = await _get_mcp_agent()
    
    prompt = f"""
You are an AI assistant connected to MCP tools (greet, reverse_string, get_current_date, calculate).

IMPORTANT:
Whenever the user asks to greet someone, reverse a string, get today's date, or perform a calculation,
ALWAYS invoke the corresponding tool. Do NOT answer yourself manually.

User request:
{question}
"""
    result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
    response = result["messages"][-1].content
    
    if isinstance(response, list):
        return response[0]["text"]
    return str(response)


def execute_mcp(question: str) -> str:
    """
    Synchronous entry point calling the existing TASK2 MCP client tool chain.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(execute_mcp_async(question))
        else:
            return asyncio.run(execute_mcp_async(question))
    except Exception:
        return asyncio.run(execute_mcp_async(question))

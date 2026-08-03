from langgraph.prebuilt import create_react_agent

from client import client
from llm import llm


async def build_graph():
    tools = await client.get_tools()

    agent = create_react_agent(
        model=llm,
        tools=tools
    )

    return agent
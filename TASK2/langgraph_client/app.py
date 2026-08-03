import asyncio

from graph import build_graph


async def main():
    agent = await build_graph()

    user_input = input("You: ")

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": """
You are an AI assistant.

IMPORTANT:
You have access to tools.
Whenever the user asks to greet someone, ALWAYS call the greet tool.
Do NOT answer yourself.

User request:
""" + user_input,
                }
            ]
        }
    )

    response = result["messages"][-1].content

    print("\nAssistant:")

    if isinstance(response, list):
        print(response[0]["text"])
    else:
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
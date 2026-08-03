"""
app.py
------
Main CLI Application entry point for Smart Router Agent.
Connects existing pdf-rag-chatbot and TASK2 MCP client via router agent.
"""

import sys
import os
import warnings
import logging

# Suppress verbose warnings and SDK logs (e.g. additionalProperties schema warnings)
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.ERROR)
for log_name in ["google", "langchain", "langchain_google_genai", "mcp", "asyncio"]:
    logging.getLogger(log_name).setLevel(logging.ERROR)

# Ensure UTF-8 output encoding for terminal compatibility across platforms
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from router import route_query
from utils import format_response


def process_question(question: str):
    """Processes user question through the Router Agent and prints output."""
    if not question.strip():
        print("⚠️  Please enter a non-empty question.")
        return

    route, tool_name, answer = route_query(question)
    print(format_response(route, tool_name, answer))


def main():
    """Main interactive terminal loop."""
    print("=" * 60)
    print("      🧠 SMART ROUTER AGENT (RAG + MCP Integration)      ")
    print("=" * 60)
    print("Ask questions about your uploaded PDF OR request MCP tool actions.")
    print("Type 'exit' or 'quit' to close.\n")

    if len(sys.argv) > 1:
        process_question(" ".join(sys.argv[1:]))
        return

    while True:
        try:
            user_input = input("Enter your question: ")
            if user_input.strip().lower() in ["exit", "quit"]:
                print("\n👋 Exiting Smart Router Agent. Goodbye!")
                break
            process_question(user_input)
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Application terminated. Goodbye!")
            break


if __name__ == "__main__":
    main()

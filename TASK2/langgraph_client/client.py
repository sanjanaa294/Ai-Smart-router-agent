import os
import sys
from langchain_mcp_adapters.client import MultiServerMCPClient

SERVER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp_server", "server.py"))

client = MultiServerMCPClient(
    {
        "greet_server": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [SERVER_PATH],
        }
    }
)
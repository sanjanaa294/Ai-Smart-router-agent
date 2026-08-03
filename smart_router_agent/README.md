# Smart Router Agent 🧠

The **Smart Router Agent** is an orchestration layer that integrates your existing **`pdf-rag-chatbot`** and **`TASK2` MCP server/client**.

It analyzes user questions and routes them to either:
1. **Existing PDF RAG Chatbot** (`pdf-rag-chatbot`) for document queries (reusing `chroma_db`, embeddings, and Gemini RAG pipeline).
2. **Existing MCP Server & LangGraph Client** (`TASK2`) for action queries (reusing FastMCP server tools and LangGraph React Agent).

---

## 📁 Architecture & Directory Structure

```
TASK3/
│
├── pdf-rag-chatbot/       # Existing RAG pipeline & Chroma vector DB
│     ├── chroma_db/
│     └── app.py
│
├── TASK2/                  # Existing MCP server & LangGraph client
│     ├── mcp_server/
│     └── langgraph_client/
│
└── smart_router_agent/    # Smart Router Integration Layer
      ├── app.py           # Main CLI interface
      ├── router.py        # Router Agent (delegates to adapters)
      ├── rag_adapter.py    # Interface to pdf-rag-chatbot
      ├── mcp_adapter.py    # Interface to TASK2 MCP client
      ├── utils.py         # Helper utilities
      ├── requirements.txt # Combined dependencies
      └── README.md        # Documentation
```

---

## ⚙️ How It Works

- **`rag_adapter.py`**: Connects directly to `pdf-rag-chatbot/chroma_db` and executes document retrieval and generation using the existing vector database.
- **`mcp_adapter.py`**: Connects directly to `TASK2/langgraph_client` and executes FastMCP tool calls via the existing LangGraph React agent.
- **`router.py`**: Inspects user queries and routes to the appropriate adapter. It generates no answers itself; it acts purely as an orchestrator.

---

## 🚀 How to Run

1. Open your terminal in the `smart_router_agent` directory:
   ```bash
   cd smart_router_agent
   ```

2. Run using your virtual environment Python:
   ```bash
   ..\TASK2\venv\Scripts\python.exe app.py
   ```

3. Type your question in the CLI!

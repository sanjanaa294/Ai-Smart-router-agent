# Workspace Analysis

## Executive Summary

This document presents a comprehensive software architecture and integration analysis for the multi-project workspace located in `TASK3/`. The workspace contains three distinct software systems built across sequential development phases:

1. **`pdf-rag-chatbot`** (Day 1): A Document Retrieval-Augmented Generation (RAG) system leveraging PyPDFLoader, RecursiveCharacterTextSplitter, Google Generative AI Embeddings (`gemini-embedding-001`), ChromaDB vector database, and ChatGoogleGenerativeAI (`gemini-3.5-flash`).
2. **`TASK2`** (Day 2): A Model Context Protocol (MCP) tool execution ecosystem comprising a FastMCP server (`mcp_server/server.py`) and a LangGraph React Agent client (`langgraph_client/`).
3. **`smart_router_agent`** (Day 3): A Planner / Query Router system built to orchestrate and direct incoming user queries to either document retrieval (RAG) or dynamic tool execution (MCP).

This report analyzes every Python script, environment configuration, dependency manifest, data pipeline, control graph, and component relationship across all three projects. It details component reusability, identifies redundant or legacy placeholder modules, maps out call graphs, and recommends an enterprise-grade, clean architecture for seamless integration without code duplication.

---

## Folder Structure

Below is the complete tree representation of the workspace:

```text
TASK3/
│
├── pdf-rag-chatbot/                  # Project 1: PDF RAG System
│   ├── .env                          # API key configuration (GOOGLE_API_KEY)
│   ├── app.py                        # Standalone RAG CLI query application
│   ├── ingest.py                     # Document ingestion pipeline (PDF -> Chunks -> ChromaDB)
│   ├── list_models.py                # Diagnostic script to list Gemini API models
│   ├── test_llm.py                   # Verification script for ChatGoogleGenerativeAI
│   ├── requirements.txt              # RAG dependency manifest
│   ├── chroma_db/                    # Persistent vector database directory
│   │   ├── chroma.sqlite3            # SQLite metadata database
│   │   └── 5f5f2ee2-85f.../          # Vector index folder
│   └── data/                         # Source document store
│       ├── Sanjana _Resume.pdf       # Indexed candidate resume
│       └── sample.pdf                # Indexed sample handbook
│
├── TASK2/                            # Project 2: MCP Server & LangGraph Client
│   ├── .env                          # Environment variables
│   ├── mcp_server/
│   │   └── server.py                 # FastMCP server exposing tool definitions
│   └── langgraph_client/
│       ├── app.py                    # Standalone MCP Client CLI loop
│       ├── client.py                 # MultiServerMCPClient stdio transport connector
│       ├── graph.py                  # LangGraph prebuilt React agent builder
│       ├── llm.py                    # Shared ChatGoogleGenerativeAI instance
│       ├── state.py                  # AgentState TypedDict definition
│       ├── list_models.py            # Diagnostic Gemini model lister
│       └── test_gemini.py            # Verification script for LLM
│
├── smart_router_agent/               # Project 3: Smart Router Orchestrator
│   ├── README.md                     # Documentation for Smart Router Agent
│   ├── app.py                        # Terminal CLI application entry point
│   ├── router.py                     # Planner / Query Router classification logic
│   ├── rag_adapter.py                # Integration adapter for pdf-rag-chatbot
│   ├── mcp_adapter.py                # Integration adapter for TASK2 MCP Client
│   ├── rag_tool.py                   # Legacy / standalone mock RAG lookup tool
│   ├── mcp_tool.py                   # Legacy / standalone mock MCP action tool
│   ├── utils.py                      # Text cleaning and response formatting helpers
│   └── requirements.txt              # Consolidated dependency manifest
│
└── WORKSPACE_ANALYSIS.md             # Complete Architectural & Integration Report
```

---

## Project Overview

| Project Name | Primary Purpose | Tech Stack | Key Capabilities |
| :--- | :--- | :--- | :--- |
| **`pdf-rag-chatbot`** | Extracted knowledge lookup from local PDF documents. | LangChain, ChromaDB, Google Gemini Embeddings, ChatGoogleGenerativeAI, PyPDF. | Ingests PDFs into vector store; performs similarity retrieval; returns grounded LLM answers with page source citations. |
| **`TASK2`** | Standardized tool execution framework using Model Context Protocol (MCP). | FastMCP, LangGraph, LangChain MCP Adapters, ChatGoogleGenerativeAI. | Serves tool functions (`greet`, `reverse_string`, `get_current_date`, `calculate`) over stdio transport; executes reasoning loops via LangGraph React agent. |
| **`smart_router_agent`** | Intent classification and routing orchestration engine. | Pure Python string matching, custom adapter integration layers. | Analyzes user queries; routes document queries to `rag_adapter` and action queries to `mcp_adapter`. |

---

## File-by-File Analysis

### 1. Project 1: `pdf-rag-chatbot`

#### `pdf-rag-chatbot/ingest.py`
* **Purpose**: Ingests PDF files from the `data/` folder, splits them into text chunks, generates vector embeddings using Google Generative AI Embeddings, and persists them into ChromaDB.
* **Responsibility**: Offline index creation for RAG lookup.
* **Inputs**: Files inside `pdf-rag-chatbot/data/*.pdf`, `GOOGLE_API_KEY` from `.env`.
* **Outputs**: Persisted vector database files in `pdf-rag-chatbot/chroma_db/`.
* **Functions**: None (procedural top-level script execution).
* **Classes**: None.
* **Dependencies**: `os`, `dotenv.load_dotenv`, `langchain_community.document_loaders.PyPDFLoader`, `langchain_text_splitters.RecursiveCharacterTextSplitter`, `langchain_google_genai.GoogleGenerativeAIEmbeddings`, `langchain_chroma.Chroma`.
* **Which files import it**: None (run directly via `python ingest.py`).
* **Which files it imports**: Standard Python & LangChain modules.
* **Internal Workflow**: Loads API key $\rightarrow$ Scans `data/` folder $\rightarrow$ Parses PDFs via `PyPDFLoader` $\rightarrow$ Splits text into 1000-char chunks with 200-char overlap $\rightarrow$ Generates embeddings via `gemini-embedding-001` $\rightarrow$ Writes to `chroma_db`.
* **External Libraries Used**: `langchain-community`, `langchain-text-splitters`, `langchain-google-genai`, `langchain-chroma`, `python-dotenv`, `pypdf`.
* **Design Quality**: High for batch ingestion; clean and straightforward procedural script.
* **Possible Improvements**: Wrap procedural logic into an ingest function (`ingest_documents()`) so it can be triggered programmatically.
* **Reusability**: High. The resulting `chroma_db` database artifact is reused directly by RAG adapters.

#### `pdf-rag-chatbot/app.py`
* **Purpose**: Standalone terminal chatbot for querying the persisted ChromaDB vector database.
* **Responsibility**: Loads vector store, handles user terminal prompts, retrieves relevant document chunks, constructs grounded prompts, calls Gemini LLM, and formats answer with source page numbers.
* **Inputs**: Terminal user questions via `input()`, `chroma_db` index, `GOOGLE_API_KEY`.
* **Outputs**: Terminal output containing LLM response text and document sources.
* **Functions**: None (contains `while True:` loop).
* **Classes**: None.
* **Dependencies**: `os`, `dotenv.load_dotenv`, `langchain_google_genai.GoogleGenerativeAIEmbeddings`, `langchain_google_genai.ChatGoogleGenerativeAI`, `langchain_chroma.Chroma`.
* **Which files import it**: None (standalone executable script).
* **Which files it imports**: Standard library and LangChain modules.
* **Internal Workflow**: Loads `.env` $\rightarrow$ Initializes `GoogleGenerativeAIEmbeddings` $\rightarrow$ Loads `Chroma` database $\rightarrow$ Creates retriever ($k=3$) $\rightarrow$ Enters prompt loop $\rightarrow$ Invoes retriever $\rightarrow$ Constructs context prompt $\rightarrow$ Calls `ChatGoogleGenerativeAI` $\rightarrow$ Extracts & prints response + sources.
* **External Libraries Used**: `langchain-google-genai`, `langchain-chroma`, `python-dotenv`.
* **Design Quality**: Simple and effective for standalone testing.
* **Possible Improvements**: Encapsulate RAG query logic inside a reusable function `query_rag(question: str) -> str`.
* **Reusability**: Logic is replicated in `smart_router_agent/rag_adapter.py`.

#### `pdf-rag-chatbot/test_llm.py`
* **Purpose**: Verification script to confirm Gemini API key validity and LLM Connectivity.
* **Responsibility**: Sends a simple `"Say Hello"` prompt to `ChatGoogleGenerativeAI(model="gemini-3.5-flash")`.
* **Inputs**: `GOOGLE_API_KEY`.
* **Outputs**: Terminal output `"Hello!"` or error traceback.
* **Functions / Classes**: None.
* **Dependencies**: `os`, `dotenv`, `langchain_google_genai`.
* **Which files import it / it imports**: Independent diagnostic tool.
* **Design Quality & Improvements**: Unit diagnostic script. Can be kept in scratch/diagnostics.
* **Reusability**: No. Diagnostic only.

#### `pdf-rag-chatbot/list_models.py`
* **Purpose**: Lists available Google Gemini models for the provided API key.
* **Responsibility**: Calls Google GenAI SDK client `client.models.list()`.
* **Inputs**: `GOOGLE_API_KEY`.
* **Outputs**: Printed list of available model names.
* **Functions / Classes**: None.
* **Dependencies**: `os`, `dotenv`, `google.genai`.
* **Design Quality & Reusability**: Diagnostic tool. Not required for runtime integration.

#### `pdf-rag-chatbot/requirements.txt`
* **Purpose**: Dependency manifest for Project 1.
* **Contents**: `langchain`, `langchain-community`, `langchain-google-genai`, `langchain-chroma`, `chromadb`, `pypdf`, `python-dotenv`.

---

### 2. Project 2: `TASK2` (MCP Server & LangGraph Client)

#### `TASK2/mcp_server/server.py`
* **Purpose**: Exposes tool functions over standard I/O (stdio) transport via FastMCP framework.
* **Responsibility**: Registers and executes MCP tools: `greet(name)`, `reverse_string(text)`, `get_current_date()`, and `calculate(expression)`.
* **Inputs**: JSON-RPC requests over stdio from MCP client.
* **Outputs**: JSON-RPC response payloads with tool results.
* **Functions**: `@mcp.tool() greet()`, `@mcp.tool() reverse_string()`, `@mcp.tool() get_current_date()`, `@mcp.tool() calculate()`.
* **Classes**: None (`FastMCP` instance `mcp`).
* **Dependencies**: `fastmcp.FastMCP`, `datetime`, `re`.
* **Which files import it**: Launched as a subprocess by `TASK2/langgraph_client/client.py`.
* **Which files it imports**: `fastmcp`, `datetime`, `re`.
* **Internal Workflow**: Initializes `FastMCP("My First MCP Server")` $\rightarrow$ Decorates tool functions $\rightarrow$ Runs stdio transport listener on `if __name__ == "__main__": mcp.run()`.
* **External Libraries Used**: `fastmcp`.
* **Design Quality**: High. Standard compliance with Model Context Protocol.
* **Possible Improvements**: Add docstrings to all tool functions for enhanced LLM tool descriptions.
* **Reusability**: Essential. Serves as the actual MCP Tool Server.

#### `TASK2/langgraph_client/client.py`
* **Purpose**: Instantiates `MultiServerMCPClient` to manage subprocess connection to `mcp_server/server.py`.
* **Responsibility**: Provides stdio transport interface between LangGraph and FastMCP server.
* **Inputs**: Path to `mcp_server/server.py` and `sys.executable`.
* **Outputs**: `MultiServerMCPClient` object (`client`).
* **Functions / Classes**: None.
* **Dependencies**: `os`, `sys`, `langchain_mcp_adapters.client.MultiServerMCPClient`.
* **Which files import it**: Imported by `TASK2/langgraph_client/graph.py`.
* **Which files it imports**: `langchain_mcp_adapters`.
* **Internal Workflow**: Computes absolute path to `server.py` $\rightarrow$ Initializes `MultiServerMCPClient` mapping server name to `sys.executable args: [SERVER_PATH]`.
* **Design Quality**: Excellent after path resolution fix (`sys.executable`).
* **Reusability**: High. Imported by MCP adapters.

#### `TASK2/langgraph_client/graph.py`
* **Purpose**: Asynchronously constructs the LangGraph React Agent.
* **Responsibility**: Fetches tools from `client.get_tools()`, binds them to `ChatGoogleGenerativeAI`, and builds the prebuilt React Agent workflow graph.
* **Inputs**: `client` from `client.py`, `llm` from `llm.py`.
* **Outputs**: Async LangGraph CompiledGraph (`agent`).
* **Functions**: `async def build_graph() -> agent`.
* **Classes**: None.
* **Dependencies**: `langgraph.prebuilt.create_react_agent`, `client.py`, `llm.py`.
* **Which files import it**: Imported by `TASK2/langgraph_client/app.py` and `smart_router_agent/mcp_adapter.py`.
* **Which files it imports**: `client.py`, `llm.py`.
* **Internal Workflow**: Awaits `client.get_tools()` $\rightarrow$ Passes `model=llm` and `tools=tools` to `create_react_agent()` $\rightarrow$ Returns executable compiled graph.
* **Design Quality**: Clean, modern LangGraph setup.
* **Reusability**: High. Central reusable entry point for MCP agent execution.

#### `TASK2/langgraph_client/app.py`
* **Purpose**: CLI application to interact with the LangGraph MCP Agent.
* **Responsibility**: Prompts user for input, formats request message, invokes `agent.ainvoke()`, and prints response.
* **Inputs**: Terminal user text.
* **Outputs**: Printed agent tool invocation result.
* **Functions**: `async def main()`.
* **Classes**: None.
* **Dependencies**: `asyncio`, `graph.build_graph`.
* **Which files import it**: Executable CLI file.
* **Design Quality**: Good standalone test harness.
* **Reusability**: Replaced by orchestrator CLI.

#### `TASK2/langgraph_client/llm.py`
* **Purpose**: Centralized instantiation of `ChatGoogleGenerativeAI` model (`gemini-3.5-flash`).
* **Responsibility**: Provides Gemini LLM configuration.
* **Inputs**: `GOOGLE_API_KEY`.
* **Outputs**: `llm` model instance.
* **Functions / Classes**: None.
* **Dependencies**: `os`, `dotenv.load_dotenv`, `langchain_google_genai.ChatGoogleGenerativeAI`.
* **Which files import it**: `TASK2/langgraph_client/graph.py`, `TASK2/langgraph_client/test_gemini.py`.
* **Reusability**: Highly reusable shared LLM provider.

#### `TASK2/langgraph_client/state.py`
* **Purpose**: TypedDict schema definition for agent state (`AgentState`).
* **Responsibility**: Defines custom state fields (`user_input: str`, `response: str`).
* **Inputs / Outputs**: Type schema definition.
* **Reusability**: Available for custom graph expansion.

#### `TASK2/langgraph_client/test_gemini.py` & `list_models.py`
* **Purpose**: Diagnostics for testing Gemini connectivity and listing models inside Project 2.

---

### 3. Project 3: `smart_router_agent`

#### `smart_router_agent/app.py`
* **Purpose**: Main terminal CLI application for the Smart Query Router system.
* **Responsibility**: Configures UTF-8 terminal encoding, suppresses SDK log noise, manages user input loop, calls `router.route_query(question)`, and displays formatted output cards.
* **Inputs**: User terminal text or command line argument (`sys.argv`).
* **Outputs**: Formatted terminal output cards indicating selected route, tool invoked, and answer.
* **Functions**: `process_question(question: str)`, `main()`.
* **Dependencies**: `sys`, `os`, `warnings`, `logging`, `router.route_query`, `utils.format_response`.
* **Design Quality**: High. Handles terminal encodings and clean user interface presentation.
* **Reusability**: Primary application entry point.

#### `smart_router_agent/router.py`
* **Purpose**: Planner / Router Agent that classifies queries and dispatches execution.
* **Responsibility**: Evaluates keywords to determine whether a prompt requires PDF RAG lookup (`RAG`) or MCP action tool execution (`MCP`).
* **Inputs**: User input question string.
* **Outputs**: Tuple `(route_name, tool_name, answer)`.
* **Functions**: `classify_query(question: str) -> str`, `route_query(question: str) -> tuple[str, str, str]`.
* **Dependencies**: `utils.clean_text`, `rag_adapter.query_rag`, `mcp_adapter.execute_mcp`.
* **Design Quality**: Simple and fast keyword-based decision engine; completely decoupled from generation logic.
* **Reusability**: Core orchestrator router module.

#### `smart_router_agent/rag_adapter.py`
* **Purpose**: Adapter interfacing `smart_router_agent` directly to `pdf-rag-chatbot`.
* **Responsibility**: Dynamically resolves paths to `pdf-rag-chatbot/chroma_db`, loads Google Generative AI Embeddings and Gemini LLM, queries ChromaDB, and returns answer + source citations.
* **Inputs**: Question string.
* **Outputs**: Formatted RAG answer string with page numbers.
* **Functions**: `query_rag(question: str) -> str`.
* **Dependencies**: `os`, `sys`, `dotenv`, `langchain_google_genai`, `langchain_chroma`.
* **Design Quality**: Excellent integration layer. Reuses existing vector DB without code duplication.
* **Reusability**: Essential adapter for RAG execution.

#### `smart_router_agent/mcp_adapter.py`
* **Purpose**: Adapter interfacing `smart_router_agent` directly to `TASK2` MCP server & client.
* **Responsibility**: Resolves paths to `TASK2/langgraph_client`, loads `build_graph()`, invokes the LangGraph React Agent, and returns the real tool response.
* **Inputs**: Question string.
* **Outputs**: Tool response string.
* **Functions**: `async execute_mcp_async(question: str) -> str`, `execute_mcp(question: str) -> str`.
* **Dependencies**: `os`, `sys`, `asyncio`, `warnings`, `logging`, `dotenv`, `nest_asyncio`, `graph.build_graph`.
* **Design Quality**: High. Handles async event loop bridging for CLI invocation.
* **Reusability**: Essential adapter for MCP execution.

#### `smart_router_agent/rag_tool.py` (Legacy / Standalone Mock)
* **Purpose**: Early prototype mock RAG lookup using a dictionary (`MOCK_KNOWLEDGE_BASE`).
* **Status**: Obsolete / Standalone prototype. Replaced by `rag_adapter.py`.
* **Recommendation**: Retain in scratch folder or remove during final cleanup.

#### `smart_router_agent/mcp_tool.py` (Legacy / Standalone Mock)
* **Purpose**: Early prototype mock MCP functions (`mcp_greet`, `mcp_date`, `mcp_calculate`, `mcp_reverse`).
* **Status**: Obsolete / Standalone prototype. Real tool execution now occurs via FastMCP in `TASK2/mcp_server/server.py`.
* **Recommendation**: Retain as standalone fallback or remove during final cleanup.

#### `smart_router_agent/utils.py`
* **Purpose**: String cleaning and output formatting helper utilities.
* **Functions**: `clean_text(text: str) -> str`, `format_response(route: str, tool_name: str, answer: str) -> str`.
* **Reusability**: Shared utility functions.

---

## PDF RAG Chatbot Architecture

```text
[PDF Documents in data/]
         │
         ▼ (PyPDFLoader)
[Document Objects]
         │
         ▼ (RecursiveCharacterTextSplitter: chunk=1000, overlap=200)
[Text Chunks]
         │
         ▼ (GoogleGenerativeAIEmbeddings: gemini-embedding-001)
[Vector Embeddings]
         │
         ▼ (ChromaDB Persist)
[chroma_db/ Vector Index]
         │
  =======▼======================================================
  RUNTIME RETRIEVAL & RESPONSE GENERATION (app.py / rag_adapter.py)
  ==============================================================
  User Question ──► VectorStore Retriever (k=3) ──► Top 3 Chunks
                                                        │
                                                        ▼
  Final Output ◄── ChatGoogleGenerativeAI ◄── Grounded Prompt
  (Answer + Sources)    (gemini-3.5-flash)    (Context + Query)
```

### Complete Execution Flow:
1. `python ingest.py` parses `Sanjana _Resume.pdf` and `sample.pdf` into chunked vectors saved in `pdf-rag-chatbot/chroma_db/`.
2. At query runtime, `rag_adapter.py` loads `Chroma(persist_directory="pdf-rag-chatbot/chroma_db", embedding_function=embeddings)`.
3. `retriever.invoke(question)` fetches the top 3 matching text chunks.
4. Chunks are formatted into a strict context prompt instructing the LLM to answer using ONLY the context.
5. `ChatGoogleGenerativeAI(model="gemini-3.5-flash")` generates the grounded response.
6. Document metadata (`source`, `page_label`) is extracted to display exact page citations.

---

## MCP Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                 smart_router_agent/app.py                   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               mcp_adapter.execute_mcp()                     │
└──────────────────────────────┬──────────────────────────────┘
                               │ (async event loop)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│          TASK2/langgraph_client/graph.build_graph()         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│         TASK2/langgraph_client/client.client                │
│    (MultiServerMCPClient stdio transport connector)         │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Spawns subprocess: sys.executable)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 TASK2/mcp_server/server.py                  │
│                     (FastMCP Server)                        │
│   Exposes: greet, reverse_string, get_current_date, calculate│
└─────────────────────────────────────────────────────────────┘
```

### Complete Execution Flow:
1. `mcp_adapter.py` calls `build_graph()` from `TASK2/langgraph_client/graph.py`.
2. `build_graph()` queries `MultiServerMCPClient` in `client.py`.
3. `client.py` spawns `TASK2/mcp_server/server.py` as a child process via `stdio` transport using `sys.executable`.
4. FastMCP registers `@mcp.tool()` functions (`greet`, `reverse_string`, `get_current_date`, `calculate`) and exposes tool definitions to the client.
5. LangGraph's `create_react_agent` binds these tool schemas to `ChatGoogleGenerativeAI`.
6. When the user asks an action query (e.g. `Greet Sanjana`), the React Agent decides to invoke the `greet` tool over stdio, receives the response, and formats the result.

---

## Smart Router Architecture

```text
                          User Terminal Input
                                  │
                                  ▼
                         smart_router_agent/app.py
                                  │
                                  ▼
                        smart_router_agent/router.py
                         (classify_query)
                                  │
             ┌────────────────────┴────────────────────┐
             │                                         │
    Matched RAG Keywords                      Matched MCP Keywords
    (pdf, resume, policy, etc.)               (greet, calculate, date, etc.)
             │                                         │
             ▼                                         ▼
   smart_router_agent/                     smart_router_agent/
     rag_adapter.py                           mcp_adapter.py
             │                                         │
             ▼                                         ▼
  pdf-rag-chatbot/chroma_db                 TASK2/mcp_server & client
     (Real PDF Vector DB)                       (Real FastMCP Server)
```

---

## Dependency Graph

```text
smart_router_agent/app.py
   ├── smart_router_agent/router.py
   │      ├── smart_router_agent/rag_adapter.py
   │      │      ├── pdf-rag-chatbot/chroma_db (Data Store)
   │      │      ├── langchain_google_genai
   │      │      └── langchain_chroma
   │      │
   │      └── smart_router_agent/mcp_adapter.py
   │             ├── TASK2/langgraph_client/graph.py
   │             │      ├── TASK2/langgraph_client/client.py
   │             │      │      └── TASK2/mcp_server/server.py (Subprocess via stdio)
   │             │      └── TASK2/langgraph_client/llm.py
   │             └── nest_asyncio
   │
   └── smart_router_agent/utils.py
```

### Dependency Findings:
* **Unnecessary Imports**: Legacy mock files (`rag_tool.py`, `mcp_tool.py`) are present in `smart_router_agent/` from initial prototypes but are bypassed by `router.py` in favor of `rag_adapter.py` and `mcp_adapter.py`.
* **Circular Dependencies**: None. The dependency flow is strictly unidirectional from `smart_router_agent` $\rightarrow$ adapters $\rightarrow$ underlying project modules.

---

## Call Graph

```text
User Question
  │
  ▼
app.py: main()
  │
  ▼
app.py: process_question(question)
  │
  ▼
router.py: route_query(question)
  │
  ├──► router.py: classify_query(question)
  │
  ├── [If Route == RAG] ──► rag_adapter.py: query_rag(question)
  │                            │
  │                            ├──► Chroma.as_retriever().invoke(question)
  │                            │
  │                            └──► ChatGoogleGenerativeAI.invoke(prompt)
  │
  └── [If Route == MCP] ──► mcp_adapter.py: execute_mcp(question)
                               │
                               ├──► mcp_adapter.py: execute_mcp_async(question)
                               │       │
                               │       ├──► graph.py: build_graph()
                               │       │       │
                               │       │       └──► client.py: client.get_tools()
                               │       │               │
                               │       │               └──► stdio -> server.py (FastMCP)
                               │       │
                               │       └──► CompiledGraph.ainvoke(messages)
                               │
                               └──► Returns response text
```

---

## Data Flow

1. **Document Data Flow**:
   `PDF Files (data/*.pdf)` $\rightarrow$ `PyPDFLoader` $\rightarrow$ `Text Chunks (1000 chars)` $\rightarrow$ `Google Embeddings (gemini-embedding-001)` $\rightarrow$ `Chroma Vector Store (chroma_db)` $\rightarrow$ `Retriever (k=3)` $\rightarrow$ `Context Prompt` $\rightarrow$ `Gemini LLM (gemini-3.5-flash)` $\rightarrow$ `Structured Answer + Source Pages`.

2. **MCP Tool Data Flow**:
   `User Request` $\rightarrow$ `LangGraph React Agent` $\rightarrow$ `Tool Schema Match` $\rightarrow$ `Stdio JSON-RPC Request` $\rightarrow$ `FastMCP Server` $\rightarrow$ `Python Tool Function (e.g. calculate)` $\rightarrow$ `Stdio JSON-RPC Response` $\rightarrow$ `LangGraph Synthesized Output`.

---

## Control Flow

1. **Program Startup**: `app.py` initializes encoding configurations, warning filters, and logger levels.
2. **Execution Order**:
   - `main()` receives user input string.
   - `process_question()` delegates to `router.route_query(question)`.
   - `route_query()` calls `classify_query(question)`.
   - If classified as `RAG`, control transfers to `rag_adapter.query_rag()`.
   - If classified as `MCP`, control transfers to `mcp_adapter.execute_mcp()`.
3. **Decision Making**: Keyword matching evaluates incoming tokens against defined set rules (`RAG_KEYWORDS` vs `MCP_KEYWORDS`).
4. **Return Values**: Adapters return formatted output strings back to `app.py`, which prints the final result card.

---

## Integration Analysis

### Can the existing projects be integrated?
**YES.** Integration has been demonstrated and verified. 

### Integration Strategy:
- **`pdf-rag-chatbot` Integration**: Rather than re-indexing documents or hardcoding answers, `rag_adapter.py` dynamically resolves the path to `pdf-rag-chatbot/chroma_db` and executes queries against the real Chroma index using the exact Gemini model configuration from Project 1.
- **`TASK2` Integration**: `mcp_adapter.py` dynamically adds `TASK2/langgraph_client` to `sys.path`, loads `build_graph()`, and executes tool actions against the real FastMCP server (`TASK2/mcp_server/server.py`).

---

## Reusable Components

| File Name | Function / Component | Purpose | Inputs | Outputs | Reusable? | Reason |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `pdf-rag-chatbot/ingest.py` | `Chroma.from_documents()` | Builds persistent vector database. | PDF files in `data/` | `chroma_db/` folder | **Yes** | Provides the actual vector database index. |
| `pdf-rag-chatbot/chroma_db/` | Vector Index Artifact | Persisted embeddings database. | Query vector | Top-k text chunks | **Yes** | Shared data store across applications. |
| `TASK2/mcp_server/server.py` | `@mcp.tool()` handlers | FastMCP tool execution engine. | Tool parameters | Tool results | **Yes** | Contains actual implementations of `greet`, `calculate`, `get_current_date`, and `reverse_string`. |
| `TASK2/langgraph_client/client.py` | `MultiServerMCPClient` | Manages MCP stdio transport subprocess. | Server path | Client tool specs | **Yes** | Handles IPC connection to FastMCP server. |
| `TASK2/langgraph_client/graph.py` | `build_graph()` | Assembles React Agent with MCP tools. | None | CompiledGraph | **Yes** | Provides full agentic tool-use capability. |
| `TASK2/langgraph_client/llm.py` | `llm` instance | Centralized LLM configuration. | API Key | ChatGoogleGenerativeAI | **Yes** | Reusable model provider. |
| `smart_router_agent/router.py` | `route_query()` | Intent routing orchestrator. | Question string | `(route, tool, answer)` | **Yes** | Core Planner router logic. |
| `smart_router_agent/rag_adapter.py` | `query_rag()` | Real RAG integration wrapper. | Question string | Answer + Sources | **Yes** | Connects router to Project 1. |
| `smart_router_agent/mcp_adapter.py` | `execute_mcp()` | Real MCP integration wrapper. | Question string | Tool Answer | **Yes** | Connects router to Project 2. |
| `smart_router_agent/utils.py` | `clean_text()`, `format_response()` | Helper utilities. | Text strings | Formatted output | **Yes** | Standard formatting utility. |

---

## Smart Router Analysis

### Status of Legacy Prototype Files:
In early development prototypes (Day 3 initial setup), `smart_router_agent/rag_tool.py` and `smart_router_agent/mcp_tool.py` contained static mock responses (e.g. static dictionary lookups or regex math string outputs).

### Integration Replacement:
- **`rag_tool.py`** $\rightarrow$ Replaced by **`rag_adapter.py`**, which connects directly to the real `pdf-rag-chatbot/chroma_db` vector database containing `Sanjana _Resume.pdf` and `sample.pdf`.
- **`mcp_tool.py`** $\rightarrow$ Replaced by **`mcp_adapter.py`**, which connects directly to the real `FastMCP` server (`TASK2/mcp_server/server.py`) via the `LangGraph` React agent.

### Current File Disposition:
- **Keep**: `app.py`, `router.py`, `rag_adapter.py`, `mcp_adapter.py`, `utils.py`, `requirements.txt`, `README.md`.
- **Legacy / Archive**: `rag_tool.py` and `mcp_tool.py` can be archived into a `scratch/` folder or retained as standalone fallback prototypes.

---

## Best Architecture Recommendation

To maintain an enterprise-grade, clean, and modular architecture across `TASK3/`, the following design pattern is recommended:

```text
smart_router_agent/  (Orchestrator Layer)
    │
    ├── app.py                 (Clean CLI Entry Point)
    ├── router.py              (Planner / Intent Classifier)
    │
    ├── adapters/              (Clean Integration Adapters)
    │     ├── rag_adapter.py   (Imports & queries pdf-rag-chatbot)
    │     └── mcp_adapter.py   (Imports & executes TASK2 LangGraph client)
    │
    └── utils.py               (Shared Helpers)
```

### Architectural Principles:
1. **Zero Code Duplication**: Do not copy vector indexing code or tool definitions into `smart_router_agent`. Rely entirely on `rag_adapter.py` and `mcp_adapter.py`.
2. **Subprocess Path Hygiene**: Always use `sys.executable` in `MultiServerMCPClient` to ensure the child FastMCP process inherits the active Python environment.
3. **Decoupled Classification**: Keep `router.py` stateless so that intent classification can be easily upgraded from simple keyword rules to an LLM-based zero-shot classifier or LangGraph conditional edge in future iterations.

---

## Code Quality Review

1. **Readability & Modularization**: Excellent. Functions are short, single-purpose, and heavily commented.
2. **Error Handling**: `app.py` gracefully handles `KeyboardInterrupt`, empty inputs, and UTF-8 encoding across Windows terminals.
3. **Path Handling**: Adapters use `os.path.abspath` and `sys.path.insert`, allowing the application to be executed from any working directory.
4. **Clean Logs**: Log noise and schema warnings (`additionalProperties`) are filtered cleanly at application startup.

---

## Risks & Mitigation

| Identified Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Missing Vector DB Index** | If `ingest.py` has not been run, `chroma_db` will be missing. | `rag_adapter.py` verifies `chroma_db` existence and provides helpful error prompt if unindexed. |
| **Subprocess Environment Mismatch** | Standard `python` command in stdio client might point to wrong global python. | Configured `sys.executable` in `client.py` to guarantee sub-process uses active virtual environment. |
| **Ambiguous Queries** | User query matching neither RAG nor MCP keywords. | Default fallback in `router.py` routes general queries to RAG search. |

---

## Final Summary

The `TASK3` workspace represents a well-structured, multi-stage AI Agent engineering setup:
- **`pdf-rag-chatbot`** provides robust document indexing and grounded generation.
- **`TASK2`** provides standard tool definitions served over Model Context Protocol and driven by a LangGraph React agent.
- **`smart_router_agent`** serves as the intelligent orchestrator connecting both subsystems into a unified, single-entry CLI interface without duplicating a single line of core logic or database code.

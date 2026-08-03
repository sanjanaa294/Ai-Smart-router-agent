"""
router.py
---------
Planner/Router Agent that inspects user questions and delegates execution
to either rag_adapter (PDF RAG system) or mcp_adapter (TASK2 MCP tool client).

No answers are generated inside this router module.
"""

from utils import clean_text
from rag_adapter import query_rag
from mcp_adapter import execute_mcp

RAG_KEYWORDS = [
    "pdf", "chapter", "document", "policy", "hod", "attendance", 
    "resume", "experience", "education", "skills", "projects",
    "section", "file", "book", "handbook", "summary"
]

MCP_KEYWORDS = [
    "greet", "hello", "hi", "reverse", "date", "today", "calculate",
    "math", "+", "*", "/", "-", "tool", "action"
]


def classify_query(question: str) -> str:
    """
    Analyzes the user question and decides whether to route to 'RAG' or 'MCP'.
    """
    cleaned = clean_text(question)
    
    # Priority check for MCP action triggers
    if any(kw in cleaned for kw in MCP_KEYWORDS):
        return "MCP"
        
    # Check for RAG document triggers
    if any(kw in cleaned for kw in RAG_KEYWORDS):
        return "RAG"
        
    # Default fallback routing: route general content questions to RAG document store
    return "RAG"


def route_query(question: str) -> tuple[str, str, str]:
    """
    Routes the user question to the appropriate adapter and returns results.
    
    Returns:
        tuple[str, str, str]: (Route Name, Tool Invoked, Answer String)
    """
    destination = classify_query(question)
    
    if destination == "MCP":
        answer = execute_mcp(question)
        return "MCP", "TASK2 MCP Client", answer
    else:
        answer = query_rag(question)
        return "RAG", "pdf-rag-chatbot", answer

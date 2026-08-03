"""
rag_tool.py - Simulated Local RAG (Retrieval-Augmented Generation) Tool.
Queries mock PDF knowledge base representing handbook/policy documents.
"""
from utils import clean_text

# Mock Document Store representing PDF document chunks
MOCK_KNOWLEDGE_BASE = {
    "attendance": "Attendance Policy (Page 4): Minimum 75% attendance required in all courses.",
    "hod": "Leadership (Page 1): HOD of Computer Science is Dr. A. Sharma. Office hours: 10 AM - 4 PM.",
    "chapter": "Chapter 2 (Page 12): Covers Neural Network Architectures (Perceptrons, Backpropagation).",
    "policy": "Policy Handbook (Page 2): Leave requests must be submitted 48 hours in advance.",
    "document": "Documentation Summary: Institute guidelines and academic policies for current academic year."
}


def query_rag(question: str) -> str:
    """Queries local document chunks based on user question."""
    cleaned_q = clean_text(question)
    for topic, content in MOCK_KNOWLEDGE_BASE.items():
        if topic in cleaned_q:
            return f"[RAG Engine] Found matching document chunk:\n-> {content}"
            
    return (
        "[RAG Engine] Document retrieved from PDF store:\n"
        "-> Institute Handbook: For specific details, refer to official PDF documentation."
    )

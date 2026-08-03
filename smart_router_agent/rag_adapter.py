"""
rag_adapter.py
--------------
Adapter module that interfaces directly with the existing RAG chatbot in pdf-rag-chatbot.
Reuses the existing Chroma vector database, embeddings, retriever, and Gemini LLM.
"""

import os
import sys
from dotenv import load_dotenv

# Path resolution to pdf-rag-chatbot directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_RAG_DIR = os.path.join(BASE_DIR, "pdf-rag-chatbot")

if PDF_RAG_DIR not in sys.path:
    sys.path.insert(0, PDF_RAG_DIR)

# Load environment variables from pdf-rag-chatbot/.env or root
load_dotenv(os.path.join(PDF_RAG_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, "TASK2", ".env"))

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma

api_key = os.getenv("GOOGLE_API_KEY")

# Load existing Vector Database from pdf-rag-chatbot/chroma_db
chroma_dir = os.path.join(PDF_RAG_DIR, "chroma_db")

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=api_key
)

vector_store = Chroma(
    persist_directory=chroma_dir,
    embedding_function=embeddings
)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=api_key,
    temperature=0
)


def query_rag(question: str) -> str:
    """
    Queries the existing RAG pipeline in pdf-rag-chatbot and returns answer with sources.
    
    Args:
        question (str): User question regarding uploaded PDF documents.
        
    Returns:
        str: Answer generated from document context and source citations.
    """
    results = retriever.invoke(question)
    
    if not results:
        return "I couldn't find the answer in the provided document."

    context = "\n\n".join(doc.page_content for doc in results)

    prompt = f"""
You are a helpful AI assistant.

Answer the user's question using ONLY the information provided in the context below.

If the answer is not present in the context, reply:
"I couldn't find the answer in the provided document."

Context:
{context}

Question:
{question}

Answer:
"""
    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        answer = response.content[0]["text"]
    else:
        answer = str(response.content)

    # Format sources from retrieved metadata
    sources = set()
    for doc in results:
        file_name = os.path.basename(doc.metadata.get("source", "Unknown"))
        page = doc.metadata.get("page_label")
        if page is None:
            page = str(doc.metadata.get("page", 0) + 1)
        sources.add((file_name, page))

    source_lines = [f"- {file_name} (Page {page})" for file_name, page in sorted(sources)]
    sources_text = "\nSources:\n" + "\n".join(source_lines) if source_lines else ""

    return f"{answer.strip()}\n{sources_text}"

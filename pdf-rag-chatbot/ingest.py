import os
import shutil

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Load environment
load_dotenv()

# Delete old vector database if it exists
if os.path.exists("chroma_db"):
    shutil.rmtree("chroma_db")

pdf_folder = "data"

documents = []

# Load all PDFs
for file in os.listdir(pdf_folder):
    if file.endswith(".pdf"):
        file_path = os.path.join(pdf_folder, file)
        print(f"Loading: {file}")

        loader = PyPDFLoader(file_path)
        pages = loader.load()

        documents.extend(pages)

        print(f"{file} -> {len(pages)} pages loaded")

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_documents(documents)

print(f"Total chunks: {len(chunks)}")

# Local embeddings (NO Gemini quota)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create Chroma DB
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="chroma_db"
)

print("\n✅ Vector Database Created Successfully!")
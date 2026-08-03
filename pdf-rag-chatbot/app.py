import os

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma

# Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Load Local Embedding Model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load Existing Vector Database
vector_store = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

print("Vector Database Loaded Successfully!")

# Create Retriever
retriever = vector_store.as_retriever(
    search_kwargs={"k": 10}
)

# Load Gemini Model
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=api_key,
    temperature=0
)

# Chat Loop
while True:

    question = input("\nAsk a question about the PDF (type 'exit' to quit): ")

    if question.lower() == "exit":
        print("Goodbye!")
        break

    # Retrieve Relevant Chunks
    results = retriever.invoke(question)

    # Create Context
    context = "\n\n".join(doc.page_content for doc in results)

    # Prompt
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

    # Get Response
    response = llm.invoke(prompt)

    # Print Answer
    print("\nAnswer:\n")

    if isinstance(response.content, list):
        print(response.content[0]["text"])
    else:
        print(response.content)

        # Print Sources
    print("\nSources:")

    sources = set()

    for doc in results:
        file_name = os.path.basename(doc.metadata.get("source", "Unknown"))

        page = doc.metadata.get("page_label")
        if page is None:
            page = str(doc.metadata.get("page", 0) + 1)

        sources.add((file_name, page))

    for file_name, page in sorted(sources):
        print(f"- {file_name} (Page {page})")
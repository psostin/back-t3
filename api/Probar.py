from langchain_community.vectorstores import Chroma
from langchain.embeddings.base import Embeddings

# Dummy embedding class to initialize Chroma (we're only retrieving embeddings here)
class DummyEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 768 for _ in texts]
    def embed_query(self, text: str) -> list[float]:
        return [0.0] * 768

CHROMA_PATH = "chroma"

def fetch_all_embeddings():
    # Initialize Chroma with DummyEmbeddings
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=DummyEmbeddings())
    
    # Fetch all documents and their embeddings
    documents = db._collection.get(include=["embeddings", "metadatas", "documents"])

    # Print each document and its embedding
    for text, embedding, metadata in zip(documents["documents"], documents["embeddings"], documents["metadatas"]):
        print("Text:", text)
        print("Embedding:", embedding)
        print("Metadata:", metadata)
        print("\n" + "-" * 40 + "\n")

fetch_all_embeddings()

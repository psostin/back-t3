import os
import shutil
import time 
import requests
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain.embeddings.base import Embeddings

CHROMA_PATH = "chroma"
DATA_PATH = "Movies"

def main():
    message = generate_data_store()
    print(message)

def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_message = save_to_chroma(chunks)
    return save_message

def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()
    return documents

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    
    split_message = f"Split {len(documents)} documents into {len(chunks)} chunks."
    print(split_message)
    return chunks

class CustomAPIEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Use the API to get embeddings for each document in texts
        return embed_texts(texts)

    def embed_query(self, text: str) -> list[float]:
        # Get embedding for a single query text
        embedding = embed_texts([text])
        return embedding[0] if embedding else [0.0] * 768  # Ensure non-empty embedding

def embed_texts(texts: list[str]) -> list[list[float]]:
    url = "http://tormenta.ing.puc.cl/api/embed"
    embeddings = []
    
    for text in texts:
        data = {
            "model": "nomic-embed-text",
            "input": text
        }
        success = False
        attempts = 0
        
        while not success:
            try:
                response = requests.post(url, json=data, timeout=120)
                response.raise_for_status()
                result = response.json()
                embedding = result.get("embeddings")
                if embedding is None:
                    raise ValueError("No embeddings found in the response.")
                
                embeddings.append(embedding)
                success = True
                print(f"Request for '{text}' completed.")
                
            except requests.exceptions.RequestException as e:
                print(f"Request failed for text: '{text}' - {e}")
                attempts += 1
                time.sleep(0.1)

        if not success:
            embeddings.append([0.0] * 768)  # Placeholder if all retries fail

        time.sleep(0.1)  # Rate limit
    if any(isinstance(sublist[0], list) for sublist in embeddings):
                    embeddings = [item for sublist in embeddings for item in sublist]
    return embeddings

def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Extract texts from chunks
    texts = [chunk.page_content for chunk in chunks]
    
    # Initialize Chroma with CustomAPIEmbeddings
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=CustomAPIEmbeddings())
    
    # Add texts to the database; embeddings are generated by CustomAPIEmbeddings
    db.add_texts(texts=texts)
    db.persist()
    
    save_message = f"Saved {len(chunks)} chunks to {CHROMA_PATH}."
    return save_message

if __name__ == "__main__":
    main()
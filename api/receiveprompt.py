from langchain_community.vectorstores import Chroma
from .load_db import CustomAPIEmbeddings

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""



def search_similar_documents(prompt_text):
    # Initialize the dummy embedding function
    embedding_function = CustomAPIEmbeddings()  # or your dummy embedding function for testing

    # Load Chroma database
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search for the 3 most similar documents
    results = db.similarity_search_with_relevance_scores(prompt_text, k=3)
   
    if len(results) == 0:
        return "Unable to find matching results."
    print("Three most similar found")

    # Prepare the context text from search results
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    

    # Initialize the model and get the response
    
    #print(results)

    
    return results

# Usage



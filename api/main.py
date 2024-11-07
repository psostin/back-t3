from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from .receiveprompt import search_similar_documents
from .request_llm import send_prompt_to_llm
from starlette.responses import JSONResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify the allowed origins, e.g., ["http://localhost:3000"]
    allow_credentials=False,
    allow_methods=["*"],  # Allow all methods, or specify: ["POST", "GET"]
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def read_root():
    
    return {"message": "Hello, World!"}


# Assuming search_similar_documents is already defined in your code
# from your_module import search_similar_documents

# Define a request model to handle the input prompt
class PromptRequest(BaseModel):
    prompt_text: str

# Define a response model if you want to structure the response more precisely
class SearchResult(BaseModel):
    page_content: str
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]

class LLMResponse(BaseModel):
    response: str  # The final concatenated response from the LLM

def format_search_results(results):
    # Extract page_content from each Document and join with separators
    context = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    return context



@app.post("/search_similar_documents", response_model=LLMResponse)
async def search_similar_documents_endpoint(request: PromptRequest):
    print("Request received:", request.prompt_text)  # For debugging
    try:
        # Step 1: Get search results
        results = search_similar_documents(request.prompt_text)

        # Ensure results are structured as expected (a list of tuples: (Document, score))
        context = "\n\n---\n\n".join([r[0].page_content for r in results if isinstance(r, tuple) and hasattr(r[0], 'page_content')])

        # Step 3: Send prompt and formatted context to LLM
        llm_response_text = send_prompt_to_llm(request.prompt_text, context)

        # Step 4: Return the response from the LLM
        return LLMResponse(response=llm_response_text)
        
    except Exception as e:
        print("Error occurred:", e)
        raise HTTPException(status_code=500, detail=str(e))







print("Hello ")



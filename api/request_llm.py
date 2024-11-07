import requests
import json

llm_url = "http://tormenta.ing.puc.cl/api/chat"

def send_prompt_to_llm(prompt, context):
    # Combine all page_content from results into a single context string
    

    # Prepare the message payload
    messages = [
        {"role": "system", "content": f"You are a movie expert and master text analizer. Use the following context to answer the following questions:\n\n{context}"},
        {"role": "user", "content": prompt}
    ]

    payload = {
        "model": "integra-LLM",
        "messages": messages,
        "temperature": 6,
        "num_ctx": 2048,
        "repeat_last_n": 10,
        "top_k": 18
    }


    full_response =""
    # Send the request to the LLM API
    response = requests.post(llm_url, json=payload, timeout= 200, stream=True)

    # Check for successful response
    for line in response.iter_lines(decode_unicode=True):
        if line:
            try:
                # Parse each line as JSON
                data = json.loads(line)
                # Concatenate the 'content' field if 'done' is False
                if not data.get("done", True):
                    full_response += data["message"]["content"]
            except json.JSONDecodeError:
                print("Error decoding JSON line:", line)

    return full_response

# Example usage


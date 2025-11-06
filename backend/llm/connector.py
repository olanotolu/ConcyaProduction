# connector.py
import requests
import json

LLM_API_URL = "http://34.73.175.64:8091/v1/chat/completions"
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"

def query_llm(prompt: str):
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(LLM_API_URL, headers=headers, data=json.dumps(payload))
    
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")
    
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()

if __name__ == "__main__":
    output = query_llm("Summarize the purpose of Concya in one short sentence.")
    print("Concya LLM says:", output)

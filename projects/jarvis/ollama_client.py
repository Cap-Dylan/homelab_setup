import requests

OLLAMA_URL = "http://192.168.0.32:11434"

def ask_ollama(prompt):
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": "llama3.1:8b-instruct-q5_K_M",
            "prompt": prompt,
            "stream": False
        }
    )
    data = response.json()
    return data["response"]

if __name__ == "__main__":
    answer = ask_ollama("Reply with one sentence only: what is 2 + 2?")
    print(answer)

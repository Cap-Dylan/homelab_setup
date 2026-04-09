import os
import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://192.168.0.32:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b-instruct-q5_K_M")


def ask_ollama(prompt):
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "think": False
        },
        timeout=120
    )
    data = response.json()
    return data["response"]


if __name__ == "__main__":
    answer = ask_ollama("Reply with one sentence only: what is 2 + 2?")
    print(answer)

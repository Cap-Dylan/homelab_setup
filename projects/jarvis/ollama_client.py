import os
import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b-instruct-q5_K_M")
OLLAMA_COLOR_MODEL = os.environ.get("OLLAMA_COLOR_MODEL", OLLAMA_MODEL)


def ask_ollama(prompt, model=None, format=None):
    """Send a prompt to Ollama. Optionally override the model or enforce output format.

    Args:
        prompt: The text prompt to send.
        model: Override the default model (e.g. for per-task routing).
        format: Set to "json" to constrain Ollama's output to valid JSON.
                This is enforced at the inference level — the model physically
                cannot produce tokens that would break JSON structure.
    """
    payload = {
        "model": model or OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
    }

    if format:
        payload["format"] = format

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json=payload,
        timeout=120,
    )
    data = response.json()
    return data["response"]


if __name__ == "__main__":
    answer = ask_ollama("Reply with one sentence only: what is 2 + 2?")
    print(answer)

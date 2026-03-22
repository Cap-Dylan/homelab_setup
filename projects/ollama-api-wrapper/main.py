from fastapi import FastAPI
import requests
import os

app = FastAPI()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://192.168.0.32:11434")

@app.get("/health")
def health():
    return {"status": "ok", "ollama_host": OLLAMA_HOST}

@app.post("/ask")
def ask(prompt: str, model: str = "llama3.2:3b"):
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        return {
            "response": response.json()["response"],
            "model": model,
            "prompt": prompt
        }
    except requests.exceptions.ConnectionError:
        return {"error": "could not reach Ollama — is it running?"}
    except requests.exceptions.Timeout:
        return {"error": "request timed out"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/summarize")
def summarize(text: str, model: str = "llama3.1:8b-instruct-q5_K_M"):
    prompt = f"Summarize the following text concisely in 3-5 sentences:\n\n{text}"
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        return {
            "summary": response.json()["response"],
            "model": model,
            "original_length": len(text)
        }
    except requests.exceptions.ConnectionError:
        return {"error": "could not reach Ollama — is it running?"}
    except requests.exceptions.Timeout:
        return {"error": "request timed out"}
    except Exception as e:
        return {"error": str(e)}
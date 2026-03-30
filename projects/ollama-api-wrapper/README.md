# ollama-api-wrapper

A lightweight FastAPI wrapper around a self-hosted Ollama instance. Exposes a clean REST API for local LLM inference — built as part of a privacy-first homelab stack with no cloud dependency.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Returns API status and configured Ollama host |
| POST | `/ask` | Proxies a prompt to Ollama, returns response + latency |
| POST | `/summarize` | Summarizes input text via Ollama, returns summary + latency |

## Setup
```bash
git clone git@github.com:Cap-Dylan/homelab_setup.git
cd homelab_setup/projects/ollama-api-wrapper
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
export OLLAMA_HOST=http://<your-ollama-ip>:11434
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Stack
- FastAPI + Uvicorn
- Ollama (local inference)
- Tailscale mesh networking

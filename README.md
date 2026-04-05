
# homelab_setup

## Overview of what's currently on station in my homelab

Multi-node, hybrid-architecture homelab optimized for local AI, IoT, and privacy-focused smart
home development. Designed for low-power 24/7 operation + heavy CUDA workloads on-demand.

**Key Design Principles**
- Privacy-first, fully local — no cloud dependency
- Repurposed consumer hardware for sustainability
- Dedicated low-power nodes for always-on services
- GPU-accelerated inference and training on separate hardware
- Modern multi-gig networking with UPS protection

(Full details in [docs/infrastructure.md](docs/infrastructure.md))

## Current Status — April 2026

| Phase | Status | Summary |
|-------|--------|---------|
| Phase 1 | ✅ | SSH config, Tailscale mesh, VS Code Remote SSH, headless Vivobook, pyenv + Python 3.11.9, GitHub SSH auth |
| Phase 2 | ✅ | README rewrite, /projects scaffolding, .gitignore, conventional commit discipline |
| Phase 3 | ✅ | FastAPI Ollama wrapper — /health, /ask, /summarize |
| Phase 4 | ✅ | IoT SSID isolation, Tapo C121 RTSP, Frigate NVR on NAS, Frigate → HA via HACS + MQTT, all detection sensors live |
| Phase 5 | ✅ | HA host monitoring in Grafana, GitHub profile README published |
| Phase 6 | ✅ | Jarvis agentic system MVP — person detected → LLM reasons → living room light controlled autonomously with brightness + time-of-day awareness |
| Phase 7 | 🔄 | Jarvis expansion: lab light automation, Frigate snapshot multimodal input, Halocode voice interface |

## Jarvis — Local Agentic Smart Home System

Jarvis is a fully local AI agent running on the Vivobook that listens for home events,
reasons about them using a local LLM on the MSI's RTX 2060, and executes actions via
the Home Assistant REST API. No cloud, no subscriptions, no data leaving the network.

**Trigger flow:**
Frigate detects occupancy → HA automation fires → REST command → Jarvis webhook →
Ollama reasons → structured JSON decision → HA executes action

**Stack:**
- Orchestrator: Python (Flask + requests) on Vivobook, running as systemd service
- Brain: llama3.1:8b-instruct-q5_K_M via Ollama on MSI GE76 (RTX 2060)
- Eyes: Tapo C121 → Frigate NVR → Home Assistant
- Hands: Home Assistant REST API

**Current capabilities:**
- Person detected → turn on living room light at context-appropriate brightness
- Occupancy cleared → turn off living room light
- Time-of-day brightness reasoning (morning/day/evening/night profiles)

**Planned:**
- Lab light automation via hallway entry detection
- Frigate snapshot → multimodal LLM visual reasoning
- Halocode voice interface with LED feedback
- Coral TPU for Frigate detection upgrade
- 27B model on tower for heavy reasoning

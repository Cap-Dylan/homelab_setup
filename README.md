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
| Phase 5 | ✅ | HA host monitoring in Grafana, all four nodes in Prometheus, GitHub profile README published |
| Phase 6 | ✅ | Jarvis agentic system — person detected → LLM reasons → living room light controlled autonomously with brightness + time-of-day awareness |
| Phase 7 | ✅ | Self-hosted Matrix chat (Continuwuity on MSI), unified 8b brain, natural language commands + conversational reasoning via Element, decision audit logging |
| Phase 8 | 🔄 | Jarvis expansion: proactive Matrix notifications, Halocode voice interface, Frigate snapshot multimodal input |

## Jarvis — Local Agentic Smart Home System

Jarvis is a fully local AI agent that controls the smart home autonomously and responds to
natural language commands via a self-hosted Matrix chat server. No cloud, no subscriptions,
no data leaving the network.

### How it works

Two input paths, one brain:

**Automated** — Frigate detects occupancy → HA automation fires → REST command → Jarvis
webhook → Ollama 8b reasons → structured JSON decision → HA executes action → decision logged

**Conversational** — You send a message in Element → Matrix bot on Vivobook receives it →
Ollama 8b reasons about intent (chat vs. command) → executes actions if needed → responds
naturally → decision logged

Both paths hit the same LLM, share the same decision log, and execute through the same
HA REST API. Everything converges.

### Stack

- **Brain**: llama3.1:8b-instruct-q5_K_M via Ollama on MSI GE76 (RTX 2060, 32GB RAM)
- **Orchestrator**: Python (Flask + requests) on Vivobook, systemd managed
- **Chat**: Continuwuity (Matrix homeserver) on MSI + Element client over Tailscale
- **Eyes**: Tapo C121 → Frigate NVR on NAS → Home Assistant
- **Hands**: Home Assistant REST API on Lenovo
- **Monitoring**: Prometheus + Grafana on Vivobook, all four nodes reporting

### Current capabilities

- Person detected → turn on living room light at context-appropriate brightness
- Occupancy cleared → turn off living room light
- Time-of-day brightness reasoning (morning 180 / day 255 / evening 150 / night 80)
- Natural language commands from Element ("turn on the lab light to an appropriate brightness")
- Conversational reasoning about past decisions ("why did you turn on the light?")
- Decision audit trail in `decisions.jsonl` with event, reasoning, and action
- `!status` for quick light state check without LLM inference

### Planned

- Proactive Matrix notifications on automated decisions
- Frigate snapshot → multimodal LLM visual reasoning
- Halocode voice interface with LED feedback
- Coral TPU for Frigate detection upgrade
- 27B model on tower for heavy reasoning tasks
- Human-in-the-loop approval for high-impact actions via Matrix
- Fine-tuned MobileNetV3/EfficientNet-Lite on 4090 for resident/delivery/unknown classification

## Hardware

| Node | Role | Always On |
|------|------|-----------|
| MSI GE76 Raider | AI inference (Ollama) + Matrix server (Continuwuity) | ✅ |
| ASUS Vivobook 16 | Infra (AdGuard, Prometheus, Grafana) + Jarvis orchestration | ✅ |
| Lenovo IdeaPad 1 | Home Assistant + MQTT + Zigbee2MQTT | ✅ |
| UGREEN NASync DXP2800 | NAS + Frigate NVR | ✅ |
| Custom Tower (4090) | Heavy ML / gaming — on-demand | ❌ |
| MacBook Pro M4 Pro | Daily driver / SSH cockpit | — |
| Surface Go 3 | Planned HA kiosk | ❌ |

## Projects

| Project | Description | Status |
|---------|-------------|--------|
| [infra-stack](projects/infra-stack) | Docker Compose stack: AdGuard, Prometheus, Grafana, Node Exporter | ✅ Live |
| [jarvis](projects/jarvis) | Agentic smart home system + Matrix chat bot | ✅ Live |
| [frigate-nvr](projects/frigate-nvr) | Frigate NVR config for Tapo C121 on NAS | ✅ Live |
| [ollama-api-wrapper](projects/ollama-api-wrapper) | FastAPI wrapper for Ollama inference | ✅ Complete |

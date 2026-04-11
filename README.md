# Homelab Setup

Multi-node, privacy-first homelab built for local AI inference, IoT automation, and smart home development. Everything runs on repurposed hardware with no cloud dependencies.

The flagship project is **Jarvis** — an agentic smart home system where Frigate person detection triggers LLM reasoning, which autonomously controls lighting based on occupancy, time of day, and weather conditions. Commands and conversation happen through a self-hosted Matrix chat interface.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Tailscale Mesh                           │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │  MSI GE76    │    │ UGREEN NAS   │    │ Lenovo IdeaPad   │   │
│  │  (Ollama)    │◄──►│  (Frigate)   │───►│ (Home Assistant)  │   │
│  │              │    │              │    │                    │   │
│  │ RTX 2060 8GB │    │ Intel N100   │    │ Zigbee2MQTT       │   │
│  │ Qwopus 9B   │    │ MQTT broker  │    │ Motion sensors     │   │
│  │ llama3.2:3b  │    │ Continuwuity │    │ Wiz smart bulbs    │   │
│  └──────────────┘    └──────────────┘    └──────────────────┘   │
│          │                   │                    ▲              │
│          │                   │                    │              │
│          ▼                   │              HA Webhooks          │
│  ┌──────────────┐            │                    │              │
│  │   Vivobook   │            │           ┌────────┴─────────┐   │
│  │ (API server) │            │           │    Jarvis Agent   │   │
│  │ FastAPI      │            │           │  Detection → LLM  │   │
│  │ Python 3.11  │            │           │   → Light Control │   │
│  └──────────────┘            │           └──────────────────┘   │
│                              │                                   │
│  ┌──────────────┐    ┌───────┴──────┐    ┌──────────────────┐   │
│  │ MacBook Pro  │    │ Custom Tower │    │  Surface Go 3    │   │
│  │  M4 Pro      │    │  RTX 4090    │    │  (planned kiosk) │   │
│  │ daily driver │    │ 128GB DDR5   │    │                  │   │
│  └──────────────┘    │ training rig │    └──────────────────┘   │
│                      └──────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

## Hardware

| Node | Role | Key Specs | OS | Status |
|------|------|-----------|----|--------|
| MSI GE76 Raider | 24/7 AI inference | i7-9750H, RTX 2060 8GB, 32GB RAM | Ubuntu Server 24.04 | Always-on |
| UGREEN NASync DXP2800 | Storage, Frigate NVR, Matrix server | Intel N100, 8GB DDR5, 2× 500GB SATA | UGOS Pro (Docker) | Always-on |
| Lenovo IdeaPad 1 | Home Assistant server | Celeron N4500, 36GB DDR4, 1TB NVMe | Home Assistant OS | Always-on |
| ASUS Vivobook 16 | API server | i5-1135G7, 8GB RAM, 512GB NVMe | Ubuntu 24.04 (headless) | Always-on |
| Custom Tower | ML training, heavy workloads | i7-14700, RTX 4090 24GB, 128GB DDR5 | Windows 11 | On-demand |
| MacBook Pro 14" | Daily driver, prototyping | M4 Pro, 24GB unified, 512GB SSD | macOS | Daily driver |
| Surface Go 3 | Planned HA kiosk | Pentium Gold, 4GB RAM | Windows | Planned |

## Networking

- **Router:** TP-Link Archer BE3600 (Wi-Fi 7, 2.5G WAN/LAN)
- **Mesh:** TP-Link Deco W6000 (wired Cat6 backhaul)
- **Overlay:** Tailscale mesh across all nodes
- **IoT isolation:** Dedicated SSID for cameras and Zigbee devices
- **Switches:** TP-Link TL-SG105S-M2 (2.5G) + TL-SG105
- **UPS:** On all critical nodes

## Project Phases

### Completed

| Phase | What Got Built |
|-------|---------------|
| 1 | SSH infrastructure, Tailscale mesh, VS Code Remote SSH, headless Vivobook setup |
| 2 | Repository structure, conventional commits, `.gitignore`, documentation baseline |
| 3 | FastAPI Ollama wrapper (`/health`, `/ask`, `/summarize`) on Vivobook |
| 4 | IoT SSID isolation, Tapo C121 RTSP stream, Frigate NVR on NAS, Frigate → HA via HACS + MQTT |
| 5 | Prometheus Node Exporter on all nodes, Grafana dashboards, GitHub profile README |
| 6 | **Jarvis v1** — person detection → LLM reasoning → autonomous light control |
| 7 | Self-hosted Matrix chat (Continuwuity), unified 8B bot for conversation + HA commands |
| 7.5 | Hardcoded on/off + brightness, weather-aware color temp, cooldown + delayed turn-off, resilient JSON parsing |
| 8 | Dockerized Jarvis (Dockerfile + docker-compose), env var config, GitHub Actions CI with smoke tests |
| 9 | Multi-model eval harness (8 models, 0.6B–9B), per-task model routing, Socratic persona, prompt engineering |

### Phase 9 Highlights

Evaluated 8 models and implemented per-task routing based on benchmarks:

| Task | Model | Latency | Accuracy |
|------|-------|---------|----------|
| Color temp reasoning | llama3.2:3b | ~800ms (warm) | 100% JSON compliance |
| Chat + commands | Qwopus3.5 9B | ~7.5s | 88% (fine-tune target) |

Key findings: 3B is the accuracy floor for reliable structured JSON. Prompt ambiguity caused more failures than model capability. Eval prompts must exactly match production prompts.

### In Progress

- **Phase 9.5** — Fine-tuning data collection: logging Qwopus failures as training pairs during normal Jarvis use (targeting 50–100 examples for QLoRA)
- **Ollama structured output** — `format: "json"` enforced at inference level to address the remaining action-drop rate

### Planned

- **Phase 10** — CV fine-tuning pipeline: MobileNetV3/EfficientNet-Lite on Frigate snapshots for resident/delivery/unknown classification (PyTorch on 4090)
- **Phase 11** — Agent v2 architecture: planner → validator → executor pipeline with goal switching and human-in-the-loop approval via Matrix
- **Phase 12** — Portfolio polish, LinkedIn, project writeups, resume bullets, interview prep

## Tech Stack

**AI/ML:** Ollama, PyTorch (planned), model evaluation, prompt engineering, per-task model routing, QLoRA fine-tuning (planned)

**Infrastructure:** Docker, Docker Compose, GitHub Actions CI, systemd, Tailscale, Prometheus, Grafana, FastAPI

**Smart Home:** Home Assistant, Zigbee2MQTT, Frigate NVR, MQTT, Wiz smart bulbs, Tapo cameras

**Communication:** Matrix (Continuwuity), nio-python

**Languages:** Python

## Key Design Principles

1. If you can write it as rules, write it as rules.
2. Separate what changes from what doesn't.
3. Make it work, make it right, make it fast — in that order.
4. Fail gracefully.
5. Don't trust user input — and LLM output is user input.
6. If you're doing something manually more than twice, automate it.
7. Name things by what they do, not how they work.
8. Log everything you'll wish you had later.
9. Keep components loosely coupled.
10. The best code is code you delete.

## Documentation

- [Infrastructure details](docs/infrastructure.md) — hardware inventory, networking, engineering notes

# homelab_setup

Privacy-first, fully local homelab. No cloud dependency. Built on repurposed consumer hardware running local AI inference, smart home automation, and IoT experimentation.

Long-term goal: a full computer vision pipeline feeding into an autonomous home automation agent.

---

## Architecture

Seven nodes, all on-prem. Three pillars: **AI inference**, **smart home control**, and **infrastructure/observability**.

| Node | Role | Always On |
|------|------|-----------|
| MacBook Pro M4 Pro | Daily driver, SSH cockpit | Yes |
| MSI GE76 Raider (RTX 2060) | LLM inference (Ollama), Matrix homeserver | Yes |
| ASUS Vivobook 16 | Infrastructure, monitoring, Jarvis orchestration | Yes |
| Lenovo IdeaPad 1 | Home Assistant OS (bare-metal), MQTT broker | Yes |
| UGREEN NASync DXP2800 (N100) | NAS, Frigate NVR, Docker apps | Yes |
| Custom Tower (RTX 4090, 128GB) | Future ML training + heavy inference | On-demand |
| Surface Go 3 | Planned HA wall kiosk | Not yet configured |

**Networking:** TP-Link BE3600 Wi-Fi 7 router, Deco W6000 mesh with Cat6 backhaul, 2.5G switches, Tailscale mesh VPN, AdGuard Home DNS, dedicated IoT SSID with device isolation.

---

## Jarvis — Autonomous Smart Home Agent

The main project. Jarvis is a multi-model AI agent that controls the smart home through two independent services:

**Automated Agent** — Frigate detects a person via the Tapo C121 camera → MQTT → Home Assistant automation → REST webhook to the Vivobook. Jarvis then makes a chain of decisions: cooldown check → hardcoded on/off → deterministic brightness lookup → LLM-reasoned color temperature → HA executes. Occupancy cleared events start a delayed turn-off with cancellation if someone comes back.

**Matrix Chat Bot** — Talk to Jarvis naturally through Element. The bot runs as a Socratic executive assistant — direct commands get immediate execution, but planning questions, architecture decisions, and "should I..." prompts get Socratic pushback to help reason through problems. Resilient JSON parsing handles when the LLM splits objects or wraps them in markdown.

### Multi-Model Routing (Phase 9)

Not every task needs the same model. I ran structured evaluations (200+ inferences across multiple test scenarios, multiple runs each) comparing JSON compliance, value accuracy, latency, and response quality across 6 models from 0.6B to 9B parameters. The accuracy floor for reliable structured JSON output was 3B — below that, models can't consistently follow schema constraints regardless of prompt engineering.

| Task | Model | Why |
|------|-------|-----|
| Color temperature | `llama3.2:3b` (~800ms avg) | Simple JSON task, 100% JSON compliance, fast |
| Chat + commands | `Qwopus3.5 9B` (~7.5s avg) | Better conversational quality, Socratic persona, fine-tuning candidate |

Decision logic philosophy: **if you can write it as rules, write it as rules.** The LLM only touches what genuinely benefits from reasoning.

| Decision | Method | Reasoning |
|----------|--------|-----------|
| Light on/off | Hardcoded Python | Can't hallucinate a boolean |
| Brightness | Time-based lookup | Pure function, no judgment needed |
| Color temperature | LLM (3B, weather-aware) | Genuinely fuzzy, benefits from reasoning |
| Chat commands | LLM (9B, full control) | User is supervising, model should interpret freely |

### Model Evaluation Methodology

Two eval harnesses in the repo:
- `eval_models.py` — Full comparison across color temp + bot command + chat scenarios with JSON compliance, latency, and per-test breakdown
- `eval_color_temp.py` — Focused color temp eval with expected value ranges, expanded boundary scenarios, and viability thresholds

Models evaluated: `llama3.1:8b`, `llama3.2:3b`, `llama3.2:1b`, `qwen2.5:1.5b`, `qwen3:0.6b`, `qwen3:1.7b`, `qwen3.5:2b`, `fredrezones55/Qwopus3.5:latest`

### Deployment

Both services run as Docker containers on the Vivobook via `docker-compose.yml`. All secrets injected through `.env` (gitignored), template in `.env.example`. GitHub Actions CI builds the image and runs smoke tests on every push to `main`. Containers run in `America/Denver` timezone.

### Key Files (`projects/jarvis/`)

| File | What it does |
|------|-------------|
| `jarvis.py` | Automated orchestrator — cooldown, delayed off, brightness lookup, LLM color temp |
| `jarvis_bot.py` | Matrix chat bot — Socratic assistant, intent parsing, command execution, conversation |
| `webhook.py` | Flask server on :5050, receives HA events |
| `ha_client.py` | Home Assistant REST API client |
| `ollama_client.py` | Ollama client with per-task model routing |
| `decision_log.py` | Writes every decision to `decisions.jsonl` |
| `eval_models.py` | Full model evaluation harness (color temp + bot) |
| `eval_color_temp.py` | Focused color temp eval with value range validation |
| `Dockerfile` | Python 3.11-slim, copies source, installs deps |
| `docker-compose.yml` | Defines jarvis-webhook + jarvis-bot containers |

---

## Monitoring Stack

Prometheus on the Vivobook scrapes all four always-on nodes every 15 seconds with 30-day retention. Grafana serves the Node Exporter Full dashboard.

| Node | Status |
|------|--------|
| Vivobook | ✅ Docker, network_mode: host |
| MSI | ✅ systemd service |
| NAS | ✅ Docker, network_mode: host |
| HA Lenovo | ✅ Community add-on |
| Tower | ⬜ Windows Node Exporter planned |

---

## Infrastructure Services (Vivobook)

Two Docker Compose stacks:

**infra-stack** — AdGuard Home (DNS sinkhole), Prometheus, Grafana, Node Exporter

**jarvis** — jarvis-webhook, jarvis-bot

Also running standalone: FastAPI Ollama wrapper with `/health`, `/ask`, `/summarize` endpoints (Phase 3, on-demand).

---

## IoT Devices

| Device | Integration | Control |
|--------|-------------|---------|
| Tapo C121 camera | Frigate (RTSP → NAS → MQTT → HA) | Jarvis automated |
| Wiz RGBWW (living room) | HA direct | Jarvis automated + Matrix chat |
| Wiz RGBWW (lab) | HA direct | Matrix chat commands |
| ThirdReality Zigbee motion sensors | Zigbee2MQTT | HA automations |
| Makeblock Halocode | Planned | Future Jarvis voice I/O |

---

## Project Timeline

| Phase | What got built |
|-------|---------------|
| 1 | SSH config, Tailscale mesh, VS Code Remote, headless Vivobook, pyenv, GitHub SSH |
| 2 | README rewrite, `/projects` scaffolding, `.gitignore`, conventional commits |
| 3 | FastAPI Ollama wrapper (`/health`, `/ask`, `/summarize`) |
| 4 | IoT SSID isolation, Tapo C121 RTSP, Frigate NVR on NAS, Frigate → HA via HACS + MQTT |
| 5 | Prometheus + Node Exporter on all nodes, Grafana dashboards, GitHub profile README |
| 6 | Jarvis v1 — person detection → LLM reasoning → autonomous light control |
| 7 | Self-hosted Matrix chat (Continuwuity), unified bot for conversation + HA commands |
| 7.5 | Hardcoded on/off + brightness, weather-aware color temp, cooldown + delayed turn-off |
| 8 | Dockerized Jarvis, env var config, GitHub Actions CI with smoke tests |
| 9 | Multi-model eval (6 models, 0.6B-9B), model routing (3B color temp, 9B Socratic chat), prompt engineering |

**Coming up:**
- Phase 10 — CV fine-tuning pipeline on the 4090 (person classification: resident / delivery / unknown)
- Phase 11 — Agent v2 architecture (planner → validator → executor, goal switching)
- Phase 12 — Portfolio polish + job prep

---

## Guiding Principles

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

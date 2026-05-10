# homelab_setup

Multi-node homelab engineered for local AI inference, smart home automation, and edge ML — with zero cloud LLM dependencies. All inference, training, and decision-making runs on owned hardware behind a Tailscale mesh.

---

## Network Architecture

```
                           ┌─────────────────────────────────────────────┐
                           │            Tailscale Mesh VPN               │
                           └──────┬──────┬──────┬──────┬──────┬─────────┘
                                  │      │      │      │      │
                    ┌─────────────┤      │      │      │      ├────────────┐
                    │             │      │      │      │      │            │
              ┌─────┴─────┐ ┌────┴────┐ │ ┌────┴────┐ │ ┌────┴────┐ ┌────┴────┐
              │   Tower   │ │   MSI   │ │ │  UGREEN │ │ │ MacBook │ │ Surface │
              │   (4090)  │ │  GE76   │ │ │   NAS   │ │ │ M4 Pro  │ │  Go 3   │
              │           │ │ (2060)  │ │ │         │ │ │         │ │         │
              │ Heavy     │ │ Light   │ │ │Syncthing│ │ │  Daily  │ │Planned  │
              │ inference │ │ 24/7    │ │ │  hub +  │ │ │ driver  │ │ kiosk   │
              │ + training│ │inference│ │ │ storage │ │ │         │ │         │
              └───────────┘ └────┬────┘ │ └─────────┘ │ └─────────┘ └─────────┘
                                 │      │             │
                          Jarvis │ ┌────┴────┐        │
                         webhook │ │ Lenovo  │        │
                                 │ │IdeaPad 1│        │
                                 │ │         │   ┌────┴────┐
                                 │ │  Home   │   │  ASUS   │
                                 │ │Assistant│   │Vivobook │
                                 │ │  + Z2M  │   │         │
                                 │ └────┬────┘   │ Docker  │
                                 │      │        │  host   │
                                 │ ┌────┴─────┐  └─────────┘
                                 │ │  Zigbee  │
                                 │ │  mesh    │
                                 │ └──────────┘
                                 │
                           ┌─────┴──────┐
                           │  Frigate   │
                           │  NVR       │
                           │ (Tapo C121)│
                           └────────────┘
```

## Hardware Inventory

| Node | Specs | OS | Role |
|------|-------|----|------|
| **Custom Tower** | i7-14700 (20C/28T), RTX 4090 24GB, 128GB DDR5, 1TB NVMe + 8TB HDD | Windows 11 | Primary inference ([`qwen3.6:35b-a3b`](https://ollama.com/library/qwen3.6:35b-a3b)), ML training, Tort Agent host |
| **MSI GE76 Raider** | i7-9750H, RTX 2060 8GB, 32GB DDR4, 500GB NVMe + 1TB HDD | Ubuntu Server 24.04 | 24/7 light inference ([`llama3.2:3b`](https://ollama.com/library/llama3.2:3b), [`qwen3.5:9b`](https://ollama.com/library/qwen3.5:9b)), Jarvis webhook host |
| **Lenovo IdeaPad 1** | Celeron N4500, 36GB DDR4, 1TB NVMe + 120GB µSD | Home Assistant OS | HA server, Zigbee2MQTT coordinator, ~10–30W idle |
| **UGREEN NASync DXP2800** | Intel N100 (4C/4T), 8GB DDR5, 2× 500GB SATA | UGOS Pro | Syncthing hub, Docker apps, vault sync source of truth |
| **MacBook Pro 14"** | M4 Pro (12C/16C GPU/16C NPU), 24GB unified, 512GB SSD | macOS | Daily driver, Tort Agent dev, Control Center dev |
| **ASUS Vivobook 16** | i5-1135G7, Iris Xe, 8GB, 512GB NVMe | Ubuntu 24.04 headless | Docker host, kiosk dashboard (deployed, standby), pyenv |
| **Surface Go 3** | Pentium Gold 6500Y, 4GB, 64GB eMMC | Windows | Planned HA kiosk display |

**Networking**: TP-Link BE3600 Wi-Fi 7 (2.5G WAN/LAN), Deco W6000 mesh (wired Cat6 backhaul), 2.5G + 1G switches, all critical nodes UPS-backed. Tailscale mesh VPN for zero-config remote access.

---

## Projects Running on This Infrastructure

### [Jarvis](https://github.com/Cap-Dylan/Jarvis) — Agentic Smart Home

Multi-zone smart home agent with two input paths (motion-triggered automation via Frigate + conversational control via Matrix) converging on a shared decision log and Home Assistant backend. Model routing validated by committed eval harnesses: `llama3.2:3b` for color-temperature decisions (~800ms, 100% JSON compliance) and `Qwen3.5:9b` for chat + tool calls (~88% accuracy). Dockerized with CI/CD via GitHub Actions, Prometheus + Grafana alerting into Matrix.

### [Jarvis Control Center](https://github.com/Cap-Dylan/control-center) — Operator Console

Full-stack ops console for real-time decision inspection, Home Assistant control, and system monitoring. FastAPI backend (Python 3.14, Pydantic v2) with 8 live endpoints serving timeline data from `decisions.jsonl`, Canvas LMS integration for academic tracking, HA REST API for direct light/automation control, and Prometheus/Node Exporter for infrastructure alerting. Vanilla React frontend (Babel-in-browser, no build step) with a Linear/Vercel-style dark dense UI. Five of six phases complete; final phase is Vivobook deployment.

### [Tort Agent](https://github.com/Cap-Dylan/tort-agent) — Local Study Assistant

Tool-calling LLM agent running `qwen3.6:35b-a3b` on the tower (RTX 4090). Six tools against an Obsidian vault: morning briefs (weather + Canvas assignments + per-class note refreshers), Apple Notes PDF export via AppleScript, handwritten note OCR (PyMuPDF + Apple Vision), atomic concept extraction with deduplication, weekly course summaries, and directory navigation. Two-mode interface — Socratic persona chat and tool-using study assistant.

### [Vault Sync](https://github.com/Cap-Dylan/vault-sync) — Local-First Obsidian Sync

Syncthing-based vault synchronization across Mac, Windows, and UGREEN NAS with automated Apple Notes export via launchd. Zero cloud subscriptions.

### [Kiosk Dashboard](https://github.com/Cap-Dylan/kiosk-dashboard) — Ambient Display

Vanilla HTML + Node.js proxy deployed to the ASUS Vivobook via SCP and systemd. Ambient display showing time, weather, Ollama model status (proxied from the tower), and quick links. Currently on standby — functionality superseded by the Control Center.

---

## Model Routing & Evaluation

Model assignments are driven by evaluation data, not assumptions. The homelab runs multiple models across nodes, each selected for a specific workload shape:

| Model | Node | Use Case | Validated By |
|-------|------|----------|-------------|
| `llama3.2:3b` | MSI (RTX 2060) | Jarvis color-temp decisions | `eval_colortemp.py` — 100% JSON compliance, <1s latency |
| `Qwen3.5:9b` | MSI (RTX 2060) | Jarvis chat + tool calls | `eval_models.py` — 88% accuracy across 8 scenarios |
| `Qwen3.5:9b` | MSI (RTX 2060) | General light inference | `eval_harness.py` — 22 tok/s, 1.0 keyword recall, 0.85 OCR quality (10 trials) |
| `qwen3.6:35b-a3b` | Tower (RTX 4090) | Tort Agent tool-use loop | Native tool calling, full model fits in 24GB VRAM |
| `qwen3.5:9b` | MacBook (M4 Pro) | Tort Agent local dev | Lighter-weight testing during development |

Eval harnesses and results are committed to their respective repositories.

---

## Infrastructure Decisions

| Decision | Rationale |
|----------|-----------|
| Bare-metal HAOS on low-power Celeron | Maximum stability, ~10W idle, no hypervisor overhead |
| MSI GE76 TDP-capped at ~60% | Efficient 24/7 inference on RTX 2060 without thermal throttling |
| UGREEN NAS over Proxmox rebuild | Intel N100 with Docker, lower maintenance than retired HP Z400 |
| Syncthing over cloud sync | End-to-end encrypted, no subscriptions, NAS as always-on hub |
| Model routing (small + large) | Deterministic tasks get fast small models; open-ended reasoning gets capable larger models |
| Tailscale mesh | Zero-config remote access, critical for multi-site operation post-relocation |

---

## Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| 10 | CV fine-tuning pipeline: Frigate snapshots → MobileNetV3/EfficientNet-Lite, QLoRA on 4090, ONNX export, containerized inference microservice | Planned |
| 11 | Agent v2: Planner/Executor/Validator architecture for multi-step task planning | Planned |
| 12 | Portfolio polish and job prep | In progress |

**Flagged automation items**: LLM log anomaly detection, Frigate snapshot → JSONL training dataset pipeline, automated homelab changelog from GitHub commits.

---

## Detailed Infrastructure

See [docs/infrastructure.md](docs/infrastructure.md) for the full hardware inventory, networking topology, software stack, and engineering decision log.

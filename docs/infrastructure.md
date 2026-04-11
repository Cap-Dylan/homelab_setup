# Homelab Infrastructure

**Last updated:** April 11, 2026
**Author:** Dylan

Current-state documentation for a multi-node homelab running local AI inference, IoT automation, and a self-hosted communication stack. No cloud dependencies — everything runs on repurposed hardware behind a Tailscale mesh.

---

## Hardware Inventory

| Node | Role | CPU / GPU | RAM | Storage | OS | Status |
|------|------|-----------|-----|---------|----|--------|
| MSI GE76 Raider | 24/7 AI inference (Ollama) | i7-9750H, RTX 2060 Super 8GB | 32GB DDR4 | 500GB NVMe + 1TB HDD | Ubuntu Server 24.04 | Always-on, TDP-capped ~60% |
| UGREEN NASync DXP2800 | Storage, Frigate NVR, Matrix server | Intel N100 (4C/4T) | 8GB DDR5 (expandable) | 2× Hitachi Deskstar 500GB (Basic mode) | UGOS Pro | Always-on |
| Lenovo IdeaPad 1 15IJL7 | Home Assistant server | Celeron N4500 (2C/2T) | 36GB DDR4 | 1TB NVMe + 120GB microSD | Home Assistant OS | Always-on, ~10–30W |
| ASUS Vivobook 16 | API server | i5-1135G7, Iris Xe | 8GB DDR4 | 512GB NVMe | Ubuntu 24.04 (headless) | Always-on |
| Custom Liquid-Cooled Tower | ML training, heavy workloads | i7-14700 (20C/28T), RTX 4090 24GB | 128GB DDR5 | 1TB NVMe + 8TB HDD | Windows 11 | On-demand |
| MacBook Pro 14" | Daily driver, prototyping | M4 Pro (12C CPU, 16C GPU, 16C NPU) | 24GB unified | 512GB SSD | macOS | Daily driver |
| Surface Go 3 | Planned HA kiosk | Pentium Gold 6500Y | 4GB | 64GB eMMC | Windows | Planned |

**Retired:** HP Z400 Workstation (Proxmox/ZFS) — removed March 2026 after repeated pve-cluster/pmxcfs failures. Replaced by UGREEN NAS.

---

## Services by Node

### MSI GE76 Raider — AI Inference

| Service | Details |
|---------|---------|
| Ollama | Primary inference server, exposed on 0.0.0.0:11434 |
| Jarvis agent | Dockerized (docker-compose), person detection → LLM reasoning → light control |
| Prometheus Node Exporter | Metrics collection for Grafana |

**Models loaded:**

| Model | Task | Latency |
|-------|------|---------|
| Qwopus3.5 9B | Chat + commands (Socratic persona) | ~7.5s |
| llama3.2:3b | Color temp reasoning | ~800ms warm |
| llama3.1:8b-instruct-q5_K_M | General inference (legacy default) | ~3s |

Ollama systemd override: `Environment="OLLAMA_HOST=0.0.0.0"` for LAN/Tailnet access.

### UGREEN NASync DXP2800 — Storage & Apps

| Service | Details |
|---------|---------|
| Frigate NVR | Tapo C121 RTSP ingestion, person detection, snapshot storage |
| Continuwuity | Self-hosted Matrix server for Jarvis chat interface |
| MQTT broker | Frigate → Home Assistant event bridge |
| Portainer | Docker container management GUI |

Drives are in Basic mode (no RAID). RAID1 planned when new drives arrive.

### Lenovo IdeaPad 1 — Home Assistant

| Service | Details |
|---------|---------|
| Home Assistant OS | Bare-metal install, primary automation hub |
| Zigbee2MQTT | Zigbee coordinator for motion sensors and smart bulbs |
| HACS | Frigate integration |
| Tailscale add-on | Mesh access (added April 2026) |

### ASUS Vivobook 16 — API Server

| Service | Details |
|---------|---------|
| FastAPI Ollama wrapper | `/health`, `/ask`, `/summarize` endpoints on port 8000 |
| pyenv | Python 3.11.9 environment management |
| Prometheus Node Exporter | Metrics collection for Grafana |

### Custom Tower — Training Rig

Currently idle. Reserved for Phase 10 (PyTorch fine-tuning on RTX 4090) and QLoRA fine-tuning of Qwopus once training data collection is complete.

---

## Networking

```
                         ┌───────────┐
                         │    ISP    │
                         └─────┬─────┘
                               │
                    ┌──────────▼───────────┐
                    │    TP-Link BE3600    │
                    │   Wi-Fi 7 Router     │
                    │   2.5G WAN/LAN       │
                    │   IoT SSID (isolated)│
                    └─────┬──────────┬─────┘
                          │          │
              ┌───────────▼──┐  ┌────▼──────────┐
              │ TL-SG105S-M2 │  │   TL-SG105    │
              │  (2.5G)      │  │   (1G)        │
              └──┬───────────┘  └───┬───────────┘
                 │                  │
        ┌────────┼──────────┐      ├── Deco W6000 (mesh node)
        │        │          │      ├── Printer
        │        │          │      └── Smart TV
        │        │          │
        │        │     Deco W6000 (mesh node)
┌───────│────────│────────────────────────────┐
│       │   ┌────┴─────────────────────────┐  │
│       │   │  Lab Infrastructure          │  │
│       │   │                              │  │
│       │   │  MSI GE76 (LAN)    (Ollama)  │  │
│       │   │  Vivobook (WIFI)    (API)    │  │
│       │   │  UGREEN NAS (LAN)  (Frigate) │  │
│       │   │  Lenovo (WIFI)       (HA)    │  │
│       │   │  Tower (LAN)       (training)│  │
│       │   └──────────────────────────────┘  │
│       │                                     │
│  Tailscale mesh overlay                     │
│  (all nodes + MacBook)                      │
└─────────────────────────────────────────────┘
```

- **Overlay:** Tailscale mesh across all nodes (MacBook, MSI, Vivobook, NAS, HA Lenovo)
- **IoT isolation:** Built into the BE3600 — dedicated SSID for cameras and Zigbee devices
- **Cabling:** Cat6 throughout the house
- **UPS:** On all critical always-on nodes
- **Measured throughput:** ~2.3 Gbps down via Ookla

---

## Smart Home / IoT Layer

| Component | Hardware | Protocol | Integration |
|-----------|----------|----------|-------------|
| Motion sensors | ThirdReality (multiple) | Zigbee | Zigbee2MQTT → HA |
| Smart bulbs | Wiz RGBWW Tunable (2) | Wi-Fi | HA REST API |
| Camera | Tapo C121 (2K QHD) | RTSP | Frigate NVR → MQTT → HA |
| Coordinator | USB Zigbee dongle | Zigbee | Zigbee2MQTT on HA |

**Automation flow:** Motion sensor triggers → HA webhook → Jarvis agent → Ollama inference → HA light service calls

---

## Engineering Decisions

| Decision | Rationale |
|----------|-----------|
| Bare-metal HA OS on low-power laptop | Ultra-stable, minimal overhead, ~10W idle draw |
| MSI GE76 TDP-capped at ~60% | Keeps thermals at 38–46°C for 24/7 operation |
| Per-task model routing | 3B for fast structured JSON, 9B for conversational quality — latency vs accuracy tradeoff |
| Ollama `format: "json"` | Enforces valid JSON at inference level, eliminating ~12% action-drop rate without fine-tuning |
| Dedicated IoT SSID | Camera and Zigbee traffic isolated from primary network |
| Tailscale over VPN | Zero-config mesh, no port forwarding, works across NAT |
| UGREEN NAS over Proxmox Z400 | Modern N100 hardware, lower power, Docker-native, no ZFS/cluster headaches |
| Dockerized Jarvis with CI | Reproducible deploys, GitHub Actions smoke tests catch regressions before they hit production |
| Decision logging (JSONL) | Jarvis can explain its own reasoning when asked — traceability for an autonomous agent |
| Fallback JSON parser retained | Defense in depth — even with `format: "json"`, never trust LLM output without validation |

---

## Monitoring

- **Prometheus Node Exporter** on MSI, Vivobook, NAS, Lenovo
- **Grafana dashboards** for CPU, memory, disk, GPU thermals, network
- **Pending:** Windows Node Exporter on tower 

---

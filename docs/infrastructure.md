# Homelab Infrastructure Documentation

**Last updated**: April 4, 2026
**Author**: Dylan (Applied AI & IoT Engineering sophomore)
**Purpose**: Full infrastructure snapshot

---

## Philosophy

Privacy-first, fully local, no cloud dependency. Built on repurposed consumer hardware. Every service runs on-prem. Designed around three pillars: local AI inference, smart home automation, and IoT experimentation. Long-term goal is a full computer vision pipeline using a fine-tuned model on the 4090, feeding into a local Jarvis-style agentic smart home system.

---

## Hardware Inventory

| Device | Role | CPU / GPU | RAM | Storage | OS | Power (idle) |
|---|---|---|---|---|---|---|
| MacBook Pro 14" M4 Pro | Daily driver / Lab cockpit | M4 Pro (12C CPU, 16C GPU, 16C NPU) | 24 GB unified | 512 GB SSD | macOS | Excellent battery |
| MSI GE76 Raider | AI Inference Server (on-demand) | i7-9750H + RTX 2060 Super 8 GB | 32 GB DDR4 | 500 GB NVMe + 1 TB HDD | Ubuntu Server 24.04 LTS (headless) | ~38–46°C |
| Custom Liquid-Cooled Tower | Heavy ML / Gaming (idle) | i7-14700 (20C/28T) + RTX 4090 24 GB | 128 GB DDR5 | 1 TB NVMe + 8 TB HDD | Windows 11 | Off unless needed |
| UGREEN NASync DXP2800 | Primary NAS, App Server & NVR | Intel N100 (4C/4T, QuickSync) | 8 GB DDR5 | 2× Hitachi 500 GB SATA (Btrfs, no RAID yet) | UGOS Pro | ~10–25 W |
| Lenovo IdeaPad 1 15IJL7 | Home Assistant Server | Celeron N4500 (2C/2T) | 36 GB DDR4 | 1 TB NVMe + 120 GB microSD | Home Assistant OS (bare-metal) | ~10–30 W |
| ASUS Vivobook 16 | Infrastructure Services Node | i5-1135G7 + Intel Iris Xe | 8 GB DDR4 | 512 GB NVMe | Ubuntu 24.04 LTS (headless, always-on) | Low |
| Surface Go 3 | Planned HA Kiosk | Pentium Gold 6500Y | 4 GB | 64 GB eMMC | Windows (kiosk mode planned) | Fanless |

**Note**: HP Z400 (Proxmox/ZFS) retired March 2026 after repeated pve-cluster/pmxcfs failures.

---

## Networking

| Component | Details |
|---|---|
| Router | TP-Link Archer BE3600 (Wi-Fi 7, 2.5G WAN/LAN) |
| Mesh | TP-Link Deco W6000 2-pack, wired Cat6 backhaul |
| Switches | TP-Link TL-SG105S-M2 (2.5G) + TL-SG105 |
| Cabling | Cat6 throughout |
| VPN Mesh | Tailscale across all nodes |
| Primary DNS | [REDACTED] (Vivobook/AdGuard), fallback 1.1.1.1 |
| UPS | Present on all critical nodes |

### IoT Isolation
Dedicated IoT/guest SSID with "Allow guests to access local network" ON (required for Frigate → camera RTSP) and "Allow guests to see each other" OFF. Device Isolation list contains Wiz bulbs and Tapo C121. Master toggle currently ON.

### Reserved IPs
| Node | IP |
|---|---|
| UGREEN NASync | [REDACTED] |
| MSI GE76 | [REDACTED] |
| Lenovo (HA) | [REDACTED] |
| Tapo C121 | [REDACTED] |
| ASUS Vivobook | [REDACTED] |

---

## Software Stack

### ASUS Vivobook — infra-stack (Docker Compose, always-on)

| Service | Port | Notes |
|---|---|---|
| AdGuard Home | 53 / 80 | Network-wide DNS sinkhole, upstream 1.1.1.1 / 9.9.9.9 |
| Prometheus | 9090 | 15s scrape interval, 30-day retention |
| Grafana | 3001 | Node Exporter Full dashboard (ID 1860), all four nodes visible |
| Node Exporter | 9100 | Host metrics via network_mode: host |
| FastAPI Ollama Wrapper | 8000 | /health, /ask, /summarize — Phase 3, on-demand |

**Prometheus scrape targets**: Vivobook (:9100), MSI (:9100), NAS (:9100), HA Lenovo (:9100)

### UGREEN NASync — Docker (via Portainer)

| Service | Notes |
|---|---|
| Portainer | Docker management GUI |
| Node Exporter | network_mode: host, reporting to Prometheus on Vivobook |
| Frigate NVR | Consuming Tapo C121 RTSP at [REDACTED]:554, N100 QuickSync decode, 1280×720 @ 5fps, MQTT → Mosquitto on HA, 7-day recording/snapshot retention, ~19% CPU / ~36% RAM steady state |

### MSI GE76 — Standalone (on-demand)

| Service | Notes |
|---|---|
| Ollama | Port 11434, llama3.1:8b-instruct-q5_K_M + llama3.2:3b. Qwen3:8b planned as primary agentic model |
| Node Exporter | systemd service, reporting to Prometheus |

### Lenovo — Home Assistant OS (always-on)

| Service | Notes |
|---|---|
| Home Assistant | Port 8123 |
| Mosquitto | MQTT broker port 1883 |
| Zigbee2MQTT | Zigbee coordinator |
| HACS | Community integration store |
| Frigate Integration | All sensors live: person count, motion, occupancy, review status, live feed |
| Prometheus Node Exporter | Community add-on (loganmarchione/hassos-addons), port 9100, reporting to Prometheus on Vivobook |

---

## Smart Home / IoT Devices

| Device | Type | Integration |
|---|---|---|
| ThirdReality sensors | Zigbee motion sensors | Zigbee2MQTT → HA |
| Wiz bulbs | Smart lighting | HA native |
| Tapo C121 | 2K camera | RTSP → Frigate → HA via HACS + MQTT |

---

## Phase Roadmap

| Phase | Status | Summary |
|---|---|---|
| Phase 1 | ✅ | SSH config, Tailscale mesh, VS Code Remote SSH, headless Vivobook, pyenv + Python 3.11.9, GitHub SSH auth |
| Phase 2 | ✅ | README rewrite, /projects scaffolding, .gitignore, conventional commit discipline |
| Phase 3 | ✅ | FastAPI Ollama wrapper — /health, /ask, /summarize, built, documented, committed |
| Phase 4 | ✅ | IoT SSID isolation, Tapo C121 RTSP verified, Frigate NVR on NAS, Frigate → HA integration via HACS + MQTT, all detection sensors live |
| Phase 5 | ✅ | Prometheus Node Exporter on HA, HA visible in Grafana (all four nodes), GitHub profile README published |
| Future | 📋 | Local Jarvis agentic system: Qwen3:8b on MSI, Python orchestrator on Vivobook consuming HA/Frigate events via REST API. Frigate CV pipeline with fine-tuned MobileNetV3/EfficientNet-Lite on 4090. Coral TPU for Frigate detection. 27B model on tower for heavy reasoning. Windows Node Exporter on tower. |

---

## Engineering Decisions & Notes

- Chose bare-metal HA OS on low-power Lenovo → ultra-stable, minimal overhead, always-on at ~10–30W
- MSI GE76 runs Ollama on-demand rather than 24/7 — started manually as needed to save power
- N100 QuickSync used for Frigate video decode on NAS → keeps CPU headroom for other services
- Retired Z400 after repeated pve-cluster/pmxcfs failures — replaced with UGREEN NASync DXP2800
- UGREEN runs Btrfs, no RAID yet — RAID1 planned when new drives arrive (2× 12TB HDD + 2× 2TB NVMe, shipping delayed)
- Tailscale + AdGuard as the networking backbone for privacy-first remote access and DNS filtering
- Open WebUI shut down — replaced by direct API access and FastAPI wrapper
- HA Prometheus integration exposes entity metrics; Node Exporter add-on exposes host metrics (CPU, RAM, disk) — both separate, only Node Exporter scrape target needed for Grafana monitoring

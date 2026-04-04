# Homelab Infrastructure — April 2026

## Hardware

### MacBook Pro 14" M4 Pro — Daily Driver / Lab Cockpit
- CPU: M4 Pro (12C CPU, 16C GPU, 16C NPU)
- RAM: 24GB unified memory
- Storage: 512GB SSD
- OS: macOS
- Role: Primary workstation, SSH cockpit into all nodes, prototyping

### MSI GE76 Raider — AI Inference Server (Always-On, Jarvis Brain)
- CPU: i7-9750H
- GPU: RTX 2060 Super 8GB VRAM
- RAM: 32GB DDR4
- Storage: 500GB NVMe + 1TB HDD
- OS: Ubuntu Server 24.04 LTS (headless)
- Role: Always-on LLM inference, dedicated Jarvis reasoning engine
- Services: Ollama on :11434
- Models: llama3.1:8b-instruct-q5_K_M (primary), llama3.2:3b (lightweight)
- Monitoring: Node Exporter → Prometheus on Vivobook

### Custom Liquid-Cooled Tower — Heavy ML / Gaming
- CPU: i7-14700 (20C/28T)
- GPU: RTX 4090 24GB VRAM
- RAM: 128GB DDR5
- Storage: 1TB NVMe + 8TB HDD
- OS: Windows 11
- Role: Idle — future PyTorch fine-tuning and 27B model inference
- Status: Off unless needed, not yet in monitoring stack

### UGREEN NASync DXP2800 — NAS, App Server & NVR
- CPU: Intel N100 (4C/4T, QuickSync capable)
- RAM: 8GB DDR5
- Storage: 2x Hitachi Deskstar 500GB SATA (RAID1 planned when new drives arrive)
- OS: UGOS Pro
- Role: Central storage, Docker host, Frigate NVR
- Services:
  - Portainer (Docker GUI)
  - Node Exporter (Docker, network_mode: host)
  - Frigate NVR — Tapo C121 RTSP, QuickSync decode, 1280x720 @ 5fps,
    MQTT → HA, 7 day retention, ~19% CPU / ~36% RAM steady state
- Notes: Btrfs, no RAID yet, RAID1 planned for incoming drives

### Lenovo IdeaPad 1 15IJL7 — Home Assistant Server
- CPU: Celeron N4500 (2C/2T)
- RAM: 36GB DDR4
- Storage: 1TB NVMe + 120GB microSD
- OS: Home Assistant OS (bare-metal)
- Role: Dedicated smart home hub, MQTT broker
- Services: Home Assistant, Zigbee2MQTT, Mosquitto, HACS,
  Prometheus Node Exporter add-on (port 9100)
- Integrations: Frigate (HACS), Zigbee devices, Wiz bulbs, Tapo C121
- Devices: ThirdReality Zigbee motion sensors, Wiz smart bulbs, Tapo C121
- Automations:
  - Jarvis Person Detected — occupancy → detected: fires rest_command.notify_jarvis
  - Jarvis Occupancy Cleared — occupancy → off: fires rest_command.notify_jarvis_clear
- Power draw: ~10–30W idle, always on

### ASUS Vivobook 16 — Infrastructure & Orchestration Node
- CPU: i5-1135G7 / Intel Iris Xe
- RAM: 8GB DDR4
- Storage: 512GB NVMe
- OS: Ubuntu 24.04 LTS (headless), sleep permanently disabled
- Role: Always-on infrastructure, observability, and Jarvis orchestration
- Services:
  - AdGuard Home — DNS sinkhole, ports 53/80
  - Prometheus — port 9090, 15s scrape, 30 day retention
  - Grafana — port 3001, Node Exporter Full (ID 1860), all four nodes
  - Node Exporter — host metrics
  - FastAPI Ollama Wrapper — /health, /ask, /summarize on :8000
  - Jarvis Agent — Flask webhook on :5050, systemd managed

### Surface Go 3 — Planned HA Kiosk
- CPU: Pentium Gold 6500Y / 4GB RAM / 64GB eMMC
- OS: Windows (kiosk mode planned)
- Role: Wall-mounted HA dashboard — not yet configured

---

## Networking
- Router: TP-Link Archer BE3600 (Wi-Fi 7, 2.5G WAN/LAN)
- Speeds: 2.3 Gbps down / 292 Mbps up
- Mesh: TP-Link Deco W6000 2-pack, wired Cat6 backhaul
- Switches: TP-Link TL-SG105S-M2 (2.5G) + TL-SG105
- VPN Mesh: Tailscale across all nodes
- DNS: Vivobook/AdGuard primary, 1.1.1.1 fallback
- UPS: Present on all critical nodes
- IoT SSID: Isolated, device isolation on Wiz bulbs + C121

---

## Devices
| Device | Location | Entity ID | Managed By |
|--------|----------|-----------|------------|
| Tapo C121 | Living room | camera.tapo_c121 | Frigate → HA |
| Wiz RGBWW 225A0A | Lab | light.wiz_rgbww_tunable_225a0a | Manual |
| Wiz RGBWW A480EC | Living room | light.wiz_rgbww_tunable_a480ec | Jarvis |
| ThirdReality motion sensors | Various | — | Zigbee2MQTT |
| Makeblock Halocode | Planned | — | Future Jarvis voice I/O |

---

## Jarvis — projects/jarvis/
| File | Purpose |
|------|---------|
| ha_client.py | HA REST API wrapper — get_state, call_service (brightness-aware) |
| ollama_client.py | Ollama REST API wrapper — targets MSI :11434 |
| jarvis.py | Core orchestrator — structured JSON decisions, time-of-day brightness |
| webhook.py | Flask event listener on :5050 |
| jarvis.service | systemd unit — enabled, restarts on failure |
| requirements.txt | requests==2.33.1, Flask==3.1.3 |

---

## Monitoring
- Prometheus scrape targets: Vivobook :9100, MSI :9100, NAS :9100, HA :9100
- Grafana dashboard: Node Exporter Full (ID 1860), all four nodes visible

---

## Future / Ongoing
- Jarvis: lab light via hallway detection, Frigate snapshot multimodal input
- Frigate CV: fine-tuned MobileNetV3/EfficientNet-Lite on 4090
- Coral TPU for Frigate detection
- 27B model on tower for heavy reasoning
- Windows Node Exporter on tower
- Halocode: microphone + LED Jarvis voice interface
- Surface Go 3: wall-mounted HA kiosk
- RAID1 on NAS when drives arrive

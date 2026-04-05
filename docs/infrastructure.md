# Homelab Infrastructure — April 2026

## Philosophy

Privacy-first, fully local, no cloud dependency. Built on repurposed consumer hardware.
Every service runs on-prem. Designed around three pillars: local AI inference, smart home
automation, and IoT experimentation.

---

## Hardware

| Node | Role | CPU | GPU | RAM | Storage | OS | Always On |
|------|------|-----|-----|-----|---------|-----|-----------|
| MacBook Pro 14" M4 Pro | Daily driver / SSH cockpit | M4 Pro (12C CPU, 16C NPU) | 16C GPU (unified) | 24GB unified | 512GB SSD | macOS | — |
| MSI GE76 Raider | AI inference + Matrix server | i7-9750H | RTX 2060 Super 8GB | 32GB DDR4 | 500GB NVMe + 1TB HDD | Ubuntu Server 24.04 LTS | ✅ |
| Custom Tower | Heavy ML / gaming — on-demand | i7-14700 (20C/28T) | RTX 4090 24GB | 128GB DDR5 | 1TB NVMe + 8TB HDD | Windows 11 | ❌ |
| UGREEN NASync DXP2800 | NAS, Docker app host, Frigate NVR | Intel N100 (4C/4T) | Intel QuickSync | 8GB DDR5 | 2x 500GB SATA (12TB HDDs + 2TB NVMe incoming) | UGOS Pro | ✅ |
| Lenovo IdeaPad 1 | Home Assistant + MQTT + Zigbee | Celeron N4500 (2C/2T) | — | 36GB DDR4 | 1TB NVMe + 120GB microSD | Home Assistant OS | ✅ |
| ASUS Vivobook 16 | Infra, monitoring, Jarvis orchestration | i5-1135G7 | Intel Iris Xe | 8GB DDR4 | 512GB NVMe | Ubuntu 24.04 LTS | ✅ |
| Surface Go 3 | Planned HA kiosk | Pentium Gold 6500Y | — | 4GB | 64GB eMMC | Windows | ❌ |

---

## Networking

- **Router**: TP-Link Archer BE3600 (Wi-Fi 7, 2.5G WAN/LAN)
- **Speeds**: 2.3 Gbps down / 292 Mbps up
- **Mesh**: TP-Link Deco W6000 2-pack, wired Cat6 backhaul
- **Switches**: TP-Link TL-SG105S-M2 (2.5G) + TL-SG105
- **Cabling**: Cat6 throughout
- **VPN mesh**: Tailscale across all nodes
- **DNS**: Vivobook/AdGuard Home primary, 1.1.1.1 fallback, set at router level
- **UPS**: Present on all critical nodes
- **IoT isolation**: Dedicated IoT/guest SSID, "Allow guests to access local network" ON (required for Frigate → camera RTSP), "Allow guests to see each other" OFF, device isolation on Wiz bulbs + C121

---

## Devices

| Device | Location | Entity ID | Managed By |
|--------|----------|-----------|------------|
| Tapo C121 | Living room | camera.tapo_c121 | Frigate → HA → Jarvis |
| Wiz RGBWW 225A0A | Lab | light.wiz_rgbww_tunable_225a0a | Jarvis (via chat) |
| Wiz RGBWW A480EC | Living room | light.wiz_rgbww_tunable_a480ec | Jarvis (automated + chat) |
| ThirdReality motion sensors | Various | — | Zigbee2MQTT |
| Makeblock Halocode | Planned | — | Future Jarvis voice I/O |

---

## Software Stack

### MSI — AI inference + chat server (always-on)

| Service | Port | Notes |
|---------|------|-------|
| Ollama | 11434 | llama3.1:8b-instruct-q5_K_M (primary), llama3.2:3b (lightweight) |
| Continuwuity | 6167 | Self-hosted Matrix homeserver, Docker, registration disabled |
| Node Exporter | 9100 | systemd service, reporting to Prometheus |

### Vivobook — infra + Jarvis orchestration (always-on)

| Service | Port | Notes |
|---------|------|-------|
| AdGuard Home | 53, 80 | Network-wide DNS sinkhole |
| Prometheus | 9090 | 15s scrape interval, 30 day retention, all four nodes |
| Grafana | 3001 | Node Exporter Full dashboard (ID 1860) |
| Node Exporter | 9100 (host) | Docker container, network_mode: host |
| Jarvis webhook | 5050 | Flask, receives HA events, systemd managed |
| Jarvis Matrix bot | — | matrix-nio, unified 8b brain, systemd managed |

### NAS — storage + NVR (always-on)

| Service | Port | Notes |
|---------|------|-------|
| Portainer | — | Docker management GUI |
| Frigate NVR | — | Tapo C121 RTSP, QuickSync decode, MQTT → HA, 7 day retention |
| Node Exporter | 9100 (host) | Docker container, network_mode: host |

NAS resource usage with Frigate: ~19% CPU / ~36% RAM steady state.

### HA (Lenovo) — smart home hub (always-on)

| Service | Port | Notes |
|---------|------|-------|
| Home Assistant | 8123 | Core smart home platform |
| Mosquitto | 1883 | MQTT broker |
| Zigbee2MQTT | — | Zigbee device coordinator |
| HACS | — | Community integration store |
| Frigate integration | — | All sensors live: person count, motion, occupancy |
| Node Exporter | 9100 | Community add-on (loganmarchione/hassos-addons) |

### HA automations

| Automation | Trigger | Action |
|------------|---------|--------|
| Jarvis Person Detected | Tapo C121 occupancy → detected | POST to Vivobook :5050/webhook, event: person_detected |
| Jarvis Occupancy Cleared | Tapo C121 occupancy → off | POST to Vivobook :5050/webhook, event: occupancy_cleared |

### HA REST commands

| Command | Target | Payload |
|---------|--------|---------|
| notify_jarvis | Vivobook :5050/webhook | event: person_detected |
| notify_jarvis_clear | Vivobook :5050/webhook | event: occupancy_cleared |

---

## Jarvis — projects/jarvis/

| File | Purpose |
|------|---------|
| webhook.py | Flask event listener on :5050 — receives HA automation events |
| jarvis.py | Automated orchestrator — fetches HA state, prompts Ollama 8b, parses JSON decision, calls HA |
| jarvis_bot.py | Matrix chat interface — unified 8b brain for conversation, commands, and reasoning |
| ha_client.py | HA REST API wrapper — get_state, call_service with brightness support |
| ollama_client.py | Ollama REST API wrapper — targets MSI :11434 |
| decision_log.py | Writes every decision to decisions.jsonl — event, reasoning, action, timestamp |
| matrix_notify.py | Posts automated decisions to the Matrix room in real time |
| jarvis.service | systemd unit for webhook — enabled, restarts on failure |
| jarvis-bot.service | systemd unit for Matrix bot — enabled, restarts on failure |
| requirements.txt | requests, Flask, matrix-nio |

### Trigger flow (automated)

Frigate detects occupancy → HA automation → REST command → Jarvis webhook →
Ollama 8b reasons → structured JSON decision → HA call_service executes →
decision logged to decisions.jsonl

### Trigger flow (conversational)

User sends message in Element → Matrix bot receives via Continuwuity →
Ollama 8b reasons about intent → executes HA actions if needed →
responds naturally → decision logged to decisions.jsonl

---

## Monitoring

- Prometheus scrape targets: Vivobook :9100, MSI :9100, NAS :9100, HA :9100
- Scrape interval: 15s across all targets
- Retention: 30 days
- Grafana dashboard: Node Exporter Full (ID 1860), all four nodes visible
- MSI at idle (Ollama + Continuwuity loaded): 0.6% CPU, 7.8% RAM

---

## Future / Ongoing

- [ ] Proactive Matrix notifications on automated Frigate decisions
- [ ] Lab light automation via hallway motion detection
- [ ] Frigate snapshot → multimodal LLM visual reasoning
- [ ] Fine-tuned MobileNetV3/EfficientNet-Lite on 4090 for resident/delivery/unknown classification
- [ ] Coral TPU for Frigate detection upgrade
- [ ] 27B model on tower for heavy reasoning tasks
- [ ] Halocode: microphone + LED Jarvis voice interface
- [ ] Human-in-the-loop approval for high-impact actions via Matrix
- [ ] Windows Node Exporter on tower when integrated
- [ ] Surface Go 3: wall-mounted HA kiosk
- [ ] RAID1 on NAS when new drives arrive

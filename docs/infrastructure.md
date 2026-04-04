# Homelab Infrastructure — April 2026

## Hardware

## Hardware

| Node | Role | CPU | GPU | RAM | Storage | OS |
|------|------|-----|-----|-----|---------|-----|
| MacBook Pro 14" M4 Pro | Daily Driver / Lab Cockpit | M4 Pro (12C CPU, 16C GPU) | 16C GPU (unified) | 24GB unified | 512GB SSD | macOS |
| MSI GE76 Raider | AI Inference — Always-On Jarvis Brain | i7-9750H | RTX 2060 Super 8GB | 32GB DDR4 | 500GB NVMe + 1TB HDD | Ubuntu Server 24.04 LTS |
| Custom Tower | Heavy ML / Gaming — Idle | i7-14700 (20C/28T) | RTX 4090 24GB | 128GB DDR5 | 1TB NVMe + 8TB HDD | Windows 11 |
| UGREEN NASync DXP2800 | NAS, App Server, NVR | Intel N100 (4C/4T) | Intel QuickSync | 8GB DDR5 | 2x 500GB SATA (RAID1 planned) | UGOS Pro |
| Lenovo IdeaPad 1 | Home Assistant Server | Celeron N4500 (2C/2T) | — | 36GB DDR4 | 1TB NVMe + 120GB microSD | Home Assistant OS |
| ASUS Vivobook 16 | Infrastructure & Orchestration | i5-1135G7 | Intel Iris Xe | 8GB DDR4 | 512GB NVMe | Ubuntu 24.04 LTS |
| Surface Go 3 | Planned HA Kiosk | Pentium Gold 6500Y | — | 4GB | 64GB eMMC | Windows |

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

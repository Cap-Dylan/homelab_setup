# Homelab Infrastructure Documentation

**Last updated**: May 2026  
**Operator**: Dylan  
**Nodes**: 7 (5 active, 1 standby, 1 planned)

---

## Hardware Inventory

| Device | CPU / GPU | RAM | Storage | OS | Role | Power |
|--------|-----------|-----|---------|----|------|-------|
| Custom Tower (liquid-cooled) | i7-14700 (20C/28T), RTX 4090 24GB | 128GB DDR5 | 1TB NVMe + 8TB HDD | Windows 11 | Primary inference, ML training | On demand |
| MSI GE76 Raider (headless) | i7-9750H, RTX 2060 8GB | 32GB DDR4 | 500GB NVMe + 1TB HDD | Ubuntu Server 24.04 | 24/7 light inference, Jarvis webhook | TDP-capped ~60% |
| Lenovo IdeaPad 1 15IJL7 | Celeron N4500 (2C/2T) | 36GB DDR4 | 1TB NVMe + 120GB µSD | Home Assistant OS | HA server, Zigbee2MQTT | ~10–30W idle |
| UGREEN NASync DXP2800 | Intel N100 (4C/4T) | 8GB DDR5 | 2× 500GB SATA + 2× M.2 (empty) | UGOS Pro | Syncthing hub, Docker apps | ~10–25W |
| MacBook Pro 14" | M4 Pro (12C/16C GPU/16C NPU) | 24GB unified | 512GB SSD | macOS | Daily driver, development | — |
| ASUS Vivobook 16 | i5-1135G7, Iris Xe | 8GB | 512GB NVMe | Ubuntu 24.04 headless | Docker host, kiosk (standby) | — |
| Surface Go 3 | Pentium Gold 6500Y | 4GB | 64GB eMMC | Windows | Planned HA kiosk | Fanless |

**Retired**: HP Z400 Workstation (Proxmox/ZFS) — retired March 2026 after repeated pve-cluster/pmxcfs failures. Replaced by UGREEN NASync DXP2800.

---

## Networking

| Component | Details |
|-----------|---------|
| Router | TP-Link Archer BE3600 (Wi-Fi 7, 2.5G WAN/LAN) — ~2.3 Gbps measured |
| Mesh | TP-Link Deco W6000 (2-pack, wired Cat6 backhaul) |
| Switches | TP-Link TL-SG105S-M2 (2.5G) + TL-SG105 (1G) |
| Cabling | Cat6 throughout |
| Power | UPS on all critical nodes |
| VPN | Tailscale mesh across all devices |
| Planned | IoT VLAN for cameras and Zigbee devices |

---

## Compute Role Matrix

| Role | Node(s) | Details |
|------|---------|---------|
| Always-on HA | Lenovo IdeaPad | Bare-metal HAOS, Zigbee2MQTT coordinator |
| Always-on inference | MSI GE76 | llama3.2:3b (Jarvis color-temp), qwen3.5:9b (Jarvis chat, eval target) |
| Heavy inference | Tower (RTX 4090) | qwen3.6:35b-a3b (Tort Agent), full model in 24GB VRAM |
| ML training | Tower (RTX 4090) | PyTorch, QLoRA fine-tuning (planned Phase 10) |
| Storage hub | UGREEN NAS | Syncthing source of truth, Docker apps |
| Dev / prototyping | MacBook M4 Pro | Tort Agent dev, Control Center dev, qwen3.5:9b local |
| Docker host | ASUS Vivobook | Kiosk dashboard (standby), containerized services |

---

## Smart Home / IoT Layer

| Component | Details |
|-----------|---------|
| Zigbee coordinator | USB dongle via Zigbee2MQTT on Lenovo |
| Motion sensors | ThirdReality Zigbee (living room + lab zones) |
| Lighting | Wiz RGBWW smart bulbs, HA REST API |
| Camera | Tapo C121 (2K QHD) → Frigate NVR → HA occupancy automations |
| Agent | Jarvis processes motion + chat through shared decision log |

---

## Software Stack

| Layer | Technology |
|-------|------------|
| Inference | Ollama (multi-node, multi-model) |
| Smart home | Home Assistant OS + Zigbee2MQTT |
| NVR | Frigate |
| Chat | Continuwuity (Matrix homeserver) + Element |
| Monitoring | Prometheus + Node Exporter + Grafana |
| Alerting | Grafana → webhook → Matrix; Control Center Prometheus integration |
| Containers | Docker + docker-compose + Portainer |
| CI/CD | GitHub Actions |
| Sync | Syncthing (vault, configs) |
| VPN | Tailscale |

---

## Model Deployment Map

| Model | Node | VRAM Usage | Workload | Eval Results |
|-------|------|-----------|----------|-------------|
| `llama3.2:3b` | MSI (RTX 2060) | ~2GB | Jarvis color-temp | 100% JSON, <1s |
| `qwen3.5:9b` | MSI (RTX 2060) | ~6GB | Jarvis chat, eval | 22 tok/s, 88% accuracy |
| `qwen3.6:35b-a3b` | Tower (RTX 4090) | ~21GB | Tort Agent | MoE, ~3B active params |
| `qwen3.5:9b` | MacBook (M4 Pro) | ~6GB | Tort Agent dev | Local development |

---

## Engineering Decisions

| Decision | Rationale |
|----------|-----------|
| Bare-metal HAOS | Maximum stability on low-power hardware, no hypervisor overhead |
| MSI TDP cap ~60% | Efficient 24/7 inference without thermal throttling |
| UGREEN NAS over Proxmox | Intel N100 mini-server with Docker, lower maintenance than Z400 |
| Syncthing over cloud | E2E encrypted, no subscriptions, NAS as always-on hub |
| Model routing | Deterministic tasks → small fast models; open-ended reasoning → capable larger models |
| Eval-driven selection | Model choices backed by committed harnesses with quantified results |
| Tailscale mesh | Zero-config remote access, critical for multi-site operation |

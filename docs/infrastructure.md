# Homelab Infrastructure

**Last updated:** April 15, 2026
**Author:** Dylan Capaldi
**Purpose:** Current baseline of the homelab — hardware, networking, compute roles, and engineering decisions.

---

## Hardware Inventory

| Device | Role | CPU / GPU | RAM | Storage | OS / Notes |
|---|---|---|---|---|---|
| **Custom Liquid-Cooled Tower** | Heavy ML training & large-model inference | i7-14700 (20C/28T) + RTX 4090 24GB | 128 GB DDR5 | 1 TB NVMe + 8 TB HDD | Windows 11 |
| **MSI GE76 Raider** (headless) | 24/7 local AI inference | i7-9750H + RTX 2060 Super 8GB | 32 GB | 500 GB NVMe + 1 TB HDD | Ubuntu Server 24.04 LTS |
| **UGREEN NASync DXP2800** | Primary NAS / app server | Intel N100 (4C/4T) | 8 GB DDR5 (expandable) | 2× 500 GB SATA + 2× M.2 NVMe slots | UGOS Pro (App Center, Docker, KVM) |
| **Lenovo IdeaPad 1 15IJL7** | Primary HA server | Celeron N4500 | 36 GB DDR4 | 1 TB NVMe + 120 GB microSD | Home Assistant OS (bare metal) |
| **Apple MacBook Pro 14"** | Daily driver / prototyping | M4 Pro (12C CPU, 16C GPU, 16C NPU) | 24 GB unified | 512 GB SSD | macOS (Ollama, MPS) |
| **ASUS Vivobook 16** | Spare / future edge device | i5-1135G7 + Iris Xe | 8 GB | 512 GB NVMe | Ubuntu 24.04 LTS |
| **Surface Go 3** | Planned HA kiosk | Pentium Gold 6500Y | 4 GB | 64 GB eMMC | TBD (kiosk mode planned) |

The legacy HP Z400 (Proxmox/ZFS) was retired in March 2026 in favor of the UGREEN NASync DXP2800 — a modern Intel N100 mini-server with built-in Docker, KVM, and 2.5 GbE networking.

---

## Networking & Connectivity

- **Primary router:** TP-Link Archer BE3600 (Wi-Fi 7, 2.5G WAN/LAN) — measured ~2.3 Gbps down
- **Mesh:** TP-Link Deco W6000 (2-pack, wired Cat6 backhaul)
- **Switches:** TP-Link TL-SG105S-M2 (2.5G) + TL-SG105
- **Cabling:** Cat6 throughout
- **Remote access:** Tailscale mesh VPN across all nodes — no public ports exposed
- **DNS:** Network-wide AdGuard Home filtering
- **UPS:** Present on all critical nodes
- **Planned:** IoT VLAN segmentation before extending camera deployment

---

## Smart Home / IoT Layer (Live)

- **Zigbee Coordinator:** MQTT-compatible dongle via Zigbee2MQTT
- **Sensors:** Multiple ThirdReality Zigbee motion sensors
- **Lighting:** Wiz RGBWW smart bulbs (motion-driven automation via Jarvis)
- **Camera:** Tapo C121 (2K QHD) → Frigate NVR → Home Assistant

---

## Compute Roles & Architecture

- **Always-on services:** Lenovo IdeaPad (Home Assistant) + MSI GE76 (Ollama inference)
- **Heavy workloads:** Custom Tower (4090) — PyTorch fine-tuning, large-model inference
- **Storage & app server:** UGREEN NASync DXP2800
- **Portability / prototyping:** MacBook M4 Pro
- **Future:** Frigate NVR consolidation onto the NASync; CV fine-tuning pipeline on the 4090

---

## Engineering Decisions & Gotchas

- **Bare-metal HA OS on a low-power laptop** — ultra-stable, minimal overhead, no virtualization layer to debug
- **MSI GE76 TDP-capped at ~60%** — perfect 24/7 inference efficiency without thermal stress
- **Retired Z400** after repeated `pve-cluster` / `pmxcfs` failures and legacy hardware frustration
- **UGOS Pro** is more capable than a typical NAS — Docker apps, VMs, direct HA/Frigate possible. ZFS not natively supported (using Btrfs for now)
- **Tailscale on every node** — no port forwards, no exposed services, every cross-node connection authenticated

---

## Project Repositories

- [`Jarvis`](https://github.com/Cap-Dylan/Jarvis) — multi-zone LLM agent for smart-home automation, runs on this lab's MSI GE76 + tower
- [`tort-agent`](https://github.com/Cap-Dylan/tort-agent) — local LLM workflow assistant, runs on the tower (RTX 4090)

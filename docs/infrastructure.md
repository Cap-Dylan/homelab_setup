# Homelab Infrastructure Documentation

**Last updated**: March 14, 2026  
**Author**: Dylan (Applied AI & IoT Engineering sophomore)  
**Purpose**: Baseline snapshot before Tapo C121 integration and Frigate rollout.

## Hardware Inventory

| Device                        | Role                                      | CPU / GPU                              | RAM          | Storage                          | OS / Notes                          | Power Draw (idle) |
|-------------------------------|-------------------------------------------|----------------------------------------|--------------|----------------------------------|-------------------------------------|-------------------|
| Lenovo IdeaPad 1 15IJL7       | Primary HA Server                         | Celeron N4500 (2C/2T)                  | 36 GB DDR4   | 1 TB NVMe + 120 GB microSD       | Home Assistant OS (bare-metal)      | ~10–30 W         |
| MSI GE76 Raider (headless)    | 24/7 Local AI Inference                   | i7-9750H + RTX 2060 Super 8 GB         | 32 GB        | 500 GB NVMe + 1 TB HDD           | Ubuntu Server 24.04 LTS             | ~38–46 °C        |
| Custom Liquid-Cooled Tower    | Heavy ML Training & Gaming                | i7-14700 (20C/28T) + RTX 4090 24 GB    | 128 GB DDR5  | 1 TB NVMe + 8 TB HDD             | Windows 11                          | Sustained loads  |
| Apple MacBook Pro 14" (M4 Pro)| Daily driver / Prototyping                | M4 Pro (12C CPU, 16C GPU, 16C NPU)     | 24 GB unified| 512 GB SSD                       | macOS (MPS / Ollama)                | 18–22+ hrs battery |
| HP Z400 Workstation           | Storage Node & Light VMs                  | Xeon W3550 (4C/8T)                     | 14 GB ECC    | 2 TB (4× SATA HDDs) ZFS pool     | Proxmox VE                          | Low              |
| Surface Go 3                  | Planned Kiosk Dashboard                   | Pentium Gold 6500Y                     | 4 GB         | 64 GB eMMC                       | Windows (kiosk mode planned)        | Fanless          |
| ASUS Vivobook 16              | Spare / Future edge device                | i5-1135G7 + Iris Xe                    | 8 GB         | 512 GB NVMe                      | Ubuntu 24.04 LTS (offline)          | —                |

## Networking & Connectivity
- Primary router: TP-Link Archer BE3600 (Wi-Fi 7, 2.5G WAN/LAN) — ~2.3 Gbps down measured via Ookala
- Mesh: TP-Link Deco W6000 (2-pack, wired Cat6 backhaul)
- Switches: TP-Link TL-SG105S-M2 (2.5G) + TL-SG105
- Cabling: Cat6 throughout house
- UPS: Present on all critical nodes
- Planned: IoT VLAN for cameras & Zigbee before Tapo integration

## Smart Home / IoT Layer (Live)
- Zigbee Coordinator: MQTT-compatible dongle via Zigbee2MQTT
- Sensors: Multiple ThirdReality Zigbee motion sensors
- Lighting: Wiz smart bulbs (fully automated with motion)
- Camera: Tapo C121 (2K QHD) — acquired, integration pending (will be first on IoT VLAN)

## Compute Roles & Architecture
- **Always-on services**: Lenovo (HA) + MSI GE76 (GPU accelerated lama3.1:8b-instruct-q5_K_M)
- **Heavy workloads**: 4090 tower (PyTorch fine-tuning for phase 9)
- **Portability / prototyping**: MacBook M4 Pro
- **Storage / backups**: Z400 Proxmox ZFS pool
- **Future**: Frigate NVR container on Z400 + 4090 passthrough for custom ML

## Decisions & Gotchas (Engineering Notes)
- Chose bare-metal HA OS on low-power laptop → ultra-stable, minimal overhead
- MSI GE76 TDP-capped at ~60 % → perfect 24/7 inference efficiency
- Z400 kept on Proxmox despite older CPU → ECC + ZFS snapshots outweigh performance
- Surface Go 3 RAM limitation noted — may upgrade to ASUS for production kiosk
- All machines behind UPS + planned Tailscale remote access

## Recommendations Completed / Pending
- [ ] Create IoT VLAN before Tapo setup
- [ ] Add monitoring (System Monitor + Glances)
- [ ] Test ZFS dataset for camera storage
- [ ] Diagram setup after Tapo integration


# Homelab Infrastructure Documentation

**Last updated**: March 14, 2026 (evening)  
**Author**: Dylan  
**Purpose**: Current baseline after retiring the legacy Z400 and bringing in the UGREEN NASync DXP2800 as the new primary storage and mini-server node.

## Hardware Inventory

| Device                          | Role                                      | CPU / GPU                              | RAM                  | Storage                                      | OS / Notes                                      | Power Draw (idle) |
|---------------------------------|-------------------------------------------|----------------------------------------|----------------------|----------------------------------------------|-------------------------------------------------|-------------------|
| Apple MacBook Pro 14" (M4 Pro)  | Daily driver / Prototyping                | M4 Pro (12C CPU, 16C GPU, 16C NPU)     | 24 GB unified       | 512 GB SSD                                   | macOS                                          | Excellent battery |
| Custom Liquid-Cooled Tower      | Heavy ML Training & Gaming                | i7-14700 + RTX 4090 24 GB              | 128 GB DDR5         | 1 TB NVMe + 8 TB HDD                         | Windows 11                                     | Sustained loads   |
| MSI GE76 Raider (headless)      | 24/7 Local AI Inference                   | i7-9750H + RTX 2060 Super 8 GB         | 32 GB               | 500 GB NVMe + 1 TB HDD                       | Ubuntu Server 24.04 LTS                        | ~38–44°C          |
| Lenovo IdeaPad 1 15IJL7         | Primary HA Server                         | Celeron N4500                          | 36 GB DDR4          | 1 TB NVMe + 120 GB microSD                   | Home Assistant OS (bare-metal)                 | ~10–30 W          |
| Surface Go 3                    | Planned Kiosk Dashboard                   | Pentium Gold 6500Y                     | 4 GB                | 64 GB eMMC                                   | Windows (kiosk mode planned)                   | Fanless           |
| ASUS Vivobook 16                | Spare / Future edge device                | i5-1135G7 + Iris Xe                    | 8 GB                | 512 GB NVMe                                  | Ubuntu 24.04 LTS (offline)                     | —                 |
| UGREEN NASync DXP2800           | Primary NAS & Mini-Server                 | Intel N100 (4C/4T)                     | 8 GB DDR5 (expandable) | 2× Hitachi Deskstar 500 GB (Basic mode) + 2× empty M.2 NVMe | UGOS Pro (App Center + Docker + VMs)           | ~10–25 W          |

**Note**: The old HP Z400 (Proxmox/ZFS) has been retired.

## Compute Roles & Architecture
- Always-on services: Lenovo (HA) + MSI GE76 (Ollama)
- Heavy workloads: 4090 tower (PyTorch fine-tuning for phase 9)
- Portability / prototyping: MacBook M4 Pro
- Primary storage & apps: UGREEN NASync DXP2800 (new central node)
- Future: Evaluate migrating HA + Frigate containers directly to NASync

## Decisions & Gotchas (Engineering Notes)
- Retired Z400 after repeated pve-cluster/pmxcfs failures and legacy hardware frustration
- Chose UGREEN NASync DXP2800 as modern replacement (Intel N100 mini-server with built-in App Center)
- Temporarily using two 15-year-old Hitachi Deskstar 500 GB SATA drives for testing (Basic mode, no RAID yet)
- Discovered UGOS Pro is much more capable than a traditional NAS (Docker apps, VMs, direct HA/Frigate possible)
- ZFS not natively supported (using Btrfs for now)


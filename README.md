# homelab_setup

## Overview of what's currently on station in my homelab

Multi-node, hybrid-architecture homelab optimized for local AI, IoT, and privacy-focused smart home development. Designed for low-power 24/7 operation + heavy CUDA workloads on-demand.

**Key Design Principles**
- Privacy-first, fully local — no cloud dependency
- Repurposed consumer hardware
- Dedicated low-power nodes for always-on services
- GPU-accelerated inference and training on separate hardware
- Modern multi-gig networking with UPS protection

(Full details in [docs/infrastructure.md](docs/infrastructure.md))

---

## Current Status — April 2026

| Phase | Status | Summary |
|---|---|---|
| Phase 1 | ✅ | SSH config, Tailscale mesh, VS Code Remote SSH, headless Vivobook, pyenv + Python 3.11.9, GitHub SSH auth |
| Phase 2 | ✅ | README rewrite, /projects scaffolding, .gitignore, conventional commit discipline |
| Phase 3 | ✅ | FastAPI Ollama wrapper — /health, /ask, /summarize |
| Phase 4 | ✅ | IoT SSID isolation, Tapo C121 RTSP, Frigate NVR on NAS, Frigate → HA via HACS + MQTT, all detection sensors live |
| Phase 5 | ✅ | HA host monitoring in Grafana, GitHub profile README |
| Future | 📋 | Local Jarvis agentic system, Frigate CV pipeline with fine-tuned model on 4090, Coral TPU, 27B model on tower |

---

## Update — April 4, 2026

**Phase 5 complete: Full observability across all four nodes**

Grafana on the Vivobook now shows CPU, RAM, and disk metrics for every node in the homelab including the Home Assistant server.

### What changed:

**Home Assistant — Prometheus Node Exporter**
- Added community add-on repo: `https://github.com/loganmarchione/hassos-addons`
- Installed **Prometheus Node Exporter** add-on on the Lenovo HA box
- Exposes host-level metrics (CPU, RAM, disk) on port 9100
- Protection Mode disabled (required for host-level access)

**Vivobook — Prometheus config updated**
- Added HA as a fourth scrape target in `prometheus.yml`:
  ```yaml
  - job_name: 'home_assistant'
    static_configs:
      - targets: ['[REDACTED]:9100']
  ```
- Restarted Prometheus via `docker compose restart prometheus`

**Grafana**
- HA node now visible in the existing Node Exporter Full dashboard (ID 1860) on `:3001`
- All four nodes reporting: Vivobook, MSI, NAS, HA Lenovo

### Notes:
- The built-in HA Prometheus integration (`prometheus:` in `configuration.yaml`) exposes entity-level metrics only — not useful for host monitoring
- Host metrics (CPU/RAM/disk) require the separate community Node Exporter add-on
- Vivobook Grafana remains the single pane of glass for all node monitoring

---

## Update — March 15, 2026

**Got local AI chat working across machines**

Today I set up OpenWebUI as an AI chat interface that runs on my UGREEN NAS but uses the GPU from my MSI GE76 laptop.

### What I got working:

* Ollama on GE76 (Ubuntu Server)
  + Fixed the service so models show up again
  + Made it listen on the whole network (0.0.0.0:11434) instead of just localhost
  + Models loaded: llama3.1:8b-instruct-q5\_K\_M and llama3.2:3b
* Portainer on UGREEN NAS
  + Installed via Docker (manual container with socket mount)
  + Gives me a web GUI to manage containers on the NAS
* Open WebUI on UGREEN NAS
  + Deployed the container using Portainer
  + Persistent storage folder: /Shared folder/docker/open-webui
  + Connected it to Ollama IP
  + Had to manually type the full IP in Open WebUI settings to make it connect
  + Tested a chat prompt → response came back using the RTX 2060 GPU

### Quick lessons from today:
* Always check `sudo ss -tuln | grep` to confirm Ollama is listening on 0.0.0.0
* Docker socket mount (/var/run/docker.sock) is required for Portainer
* Open WebUI sometimes ignores env vars on first boot → manual URL entry in settings fixed it

---

## Homelab Update — March 14, 2026

**Major hardware pivot**: Retired the legacy Z400 (Proxmox/ZFS struggles) in favor of a **UGREEN NASync DXP2800** as the dedicated storage and app server.

### UGREEN NASync DXP2800 (new central storage node)

* **Hardware**: Intel N100, 8 GB DDR5 (upgradable), 2× SATA bays + 2× M.2 NVMe
* **Drives installed**: 2× Hitachi Deskstar 500 GB in Basic mode (no RAID yet)
* **OS**: UGOS Pro
* **Key discoveries**: Effectively a mini-server with built-in App Center (HA, Frigate, Ollama, Plex, etc.), Docker support, KVM VMs, 2.5 GbE networking
* **Initial setup**: Created storage pool, shared folder "ha-frigate", enabled NFS service

**Status**: NAS UI accessible locally | Shares configured | Ready for HA integration

---

## About

Overview of what's currently on station in my homelab.

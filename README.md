# homelab_setup

A privacy-first, multi-node homelab running fully local AI inference, 
smart home automation, and IoT experimentation — no cloud dependency. 
Built on repurposed consumer hardware featuring a dedicated GPU inference 
server (RTX 2060), a 4090-equipped training rig, self-hosted LLM chat via 
Open WebUI + Ollama, a local RAG pipeline using nomic-embed-text, and Home 
Assistant controlling a full Zigbee smart home stack.

## Key design principles
- Everything runs locally — no data leaves the house
- Repurposed consumer hardware for sustainability
- Tiered compute — always-on inference separated from heavy training
- Privacy-first smart home with no cloud-dependent devices

(Full details in [docs/infrastructure.md](docs/infrastructure.md))

## Homelab Update – March 14, 2026

**Major hardware pivot tonight**: Retired the legacy  Z400 (Proxmox/ZFS struggles) in favor of a **UGREEN NASync DXP2800** as the dedicated storage & app server.

### UGREEN NASync DXP2800 (new central storage node)
- **Hardware**: Intel N100, 8 GB DDR5 (upgradable), 2× SATA bays + 2× M.2 NVMe
- **Drives installed**: 2× Hitachi Deskstar 500 GB (HDS721050CLA362 variants) in Basic mode (no RAID yet)
- **OS**: UGOS Pro
- **Key discoveries**: This is effectively a mini-server with:
  - Built-in App Center (Home Assistant, Frigate, Ollama, Plex, etc.)
  - Docker support
  - KVM VMs (limited)
  - 2.5 GbE networking
- **Initial setup**: Created storage pool, shared folder "ha-frigate", enabled NFS service
- **Next**: Mount NFS share in current HA instance → test Frigate clip storage
- **Long-term plan**: Evaluate migrating HA + Frigate containers directly to NASync (single-box consolidation)

**Status**: NAS UI accessible locally | Shares configured | Ready for HA integration tomorrow


## Update – March 15, 2026  
**Got local AI chat working across machines**

Today I set up OpenwebUI as an AI chat interface that runs on my UGREEN NAS but uses the GPU from my MSI GE76 laptop.

### What I got working:
- Ollama on GE76 (Ubuntu Server)  
  - Fixed the service so models show up again  
  - Made it listen on the whole network (0.0.0.0:11434) instead of just localhost  
  - Models loaded: llama3.1:8b-instruct-q5_K_M and llama3.2:3b

- Portainer on UGREEN NAS  
  - Installed via Docker (manual container with socket mount)  
  - Gives me a web GUI to manage containers on the NAS

- Open WebUI on UGREEN NAS  
  - Deployed the container using Portainer  
  - Persistent storage folder: /Shared folder/docker/open-webui  
  - Connected it to Ollama IP  
  - Had to manually type the full IP in Open WebUI settings to make it connect  
  - Tested a chat prompt → response came back using the RTX 2060 GPU

### Quick lessons from today:
- Always check `sudo ss -tuln | grep ` to confirm Ollama is listening on 0.0.0.0
- Docker socket mount (/var/run/docker.sock) is required for Portainer
- Open WebUI sometimes ignores env vars on first boot → manual URL entry in settings fixed it

Next up:  
- Add more models to Ollama  
- Explore uploading documents/RAG in Open WebUI
- Explore fine tuning possibilities 

  

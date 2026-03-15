# homelab_setup
## Overview of what's currently on station in my homelab
### Current Homelab Infrastructure (March 2026 Baseline)

Multi-node, hybrid-architecture homelab optimized for local AI, IoT, and privacy-focused smart home development. Designed for low-power 24/7 operation + heavy CUDA workloads.

**Key Design Principles**  
- Repurposed hardware for sustainability  
- Dedicated low-power HA server  
- GPU-accelerated inference & training separation  
- ZFS storage + ECC where possible  
- Modern multi-gig networking with UPS protection

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

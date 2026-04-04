# frigate-nvr

Frigate NVR container running on the UGREEN NASync DXP2800, consuming a 
local RTSP stream from a Tapo C121 camera and feeding motion/object detection 
events into Home Assistant.

## Key design principles
- Fully local — no cloud, no Tapo cloud dependency
- Hardware-accelerated video decode via N100 Intel QuickSync
- Camera on isolated IoT SSID, Frigate pulls stream over local network
- Detection events surface in HA as native Frigate integration events

## Camera

- **Model**: TP-Link Tapo C121
- **IP**: [REDACTED] (DHCP reserved)
- **Resolution**: 2560x1440
- **RTSP URL**: see `.env` (never committed)
- **Network**: IoT/guest SSID with local network access enabled on BE3600

## Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

Never commit `.env` — it's in `.gitignore`.

## Setup – April 3, 2026

**RTSP stream verified from Mac**

Confirmed the Tapo C121 RTSP stream is accessible on the local network.

### What was required:
- Enabled "3rd party compatibility" in Tapo app (this is the RTSP toggle)
- Created a separate RTSP account in Tapo app (distinct from main Tapo login)
- Enabled "Allow guests to access local network" on BE3600 guest SSID
- Reserved camera IP at [REDACTED] in router DHCP

### Verified with:
```bash
ffmpeg -i '$CAMERA_RTSP_URL' -frames:v 1 -update 1 ~/test.jpg
```

Stream confirmed: H264, 2560x1440 @ ~19.92fps. SEI type 764 warnings are 
harmless — Tapo firmware quirk, Frigate handles it fine.

### Network isolation notes:
- C121 is listed under Advanced → Security → Device Isolation on BE3600
- Device Isolation master toggle is currently OFF
- Plan: once Frigate is confirmed working, enable Device Isolation and 
  remove C121 from the list (NAS needs to reach it), keeping Wiz bulbs isolated

## Next Steps
- [ ] Deploy Frigate container on NAS via Portainer
- [ ] Configure frigate.yml with RTSP URL and N100 QuickSync decode
- [ ] Verify detections surfacing in Frigate web UI
- [ ] Connect Frigate to Home Assistant via native integration

## Update – April 3, 2026

**Frigate → Home Assistant integration complete**

### What was configured:
- Deployed Frigate container on UGREEN NASync via Portainer
- Enabled MQTT in frigate config pointing at Mosquitto broker on HA (Lenovo)
- Installed HACS on Home Assistant
- Installed Frigate integration via HACS
- All sensors reporting in HA: motion, person count, occupancy, review status

### Gotchas:
- Frigate integration requires HACS — not available in default HA integration store
- Mosquitto requires auth — Frigate config needs explicit mqtt user/password
- Detection resolution dropped from 2560x1440 → 1280x720 for CPU detector performance
- SEI type 764 warnings in ffmpeg output are harmless Tapo firmware quirk

### NAS resource usage with Frigate running (N100):
- CPU: ~18%
- RAM: ~37%
- Comfortable headroom remaining

### config.example.yml
See config.example.yml for full Frigate configuration template.
Real config lives at ~/frigate/config/config.yml on the NAS (gitignored).

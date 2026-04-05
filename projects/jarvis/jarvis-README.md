# jarvis

Fully local agentic smart home system. Listens for events from Frigate NVR via 
Home Assistant, reasons about them using a local LLM, and executes actions 
autonomously. No cloud, no subscriptions, no data leaving the network.

## How it works

Frigate detects occupancy → HA automation fires REST command → Jarvis webhook 
receives event → Ollama reasons about state + time of day → structured JSON 
decision → HA REST API executes action → decision logged + posted to Matrix room

## Files

| File | Role |
|------|------|
| `webhook.py` | Flask server on :5050 — receives events from HA REST commands |
| `jarvis.py` | Core orchestrator — fetches HA state, prompts Ollama, parses JSON decision, calls HA service |
| `ha_client.py` | Home Assistant REST API wrapper — `get_state`, `call_service` with brightness support |
| `ollama_client.py` | Ollama REST API wrapper — targets MSI on :11434 |
| `decision_log.py` | Writes every decision to `decisions.jsonl` — event, reasoning, action, timestamp |
| `matrix_notify.py` | Posts decisions to the Jarvis Matrix room in real time |
| `jarvis_bot.py` | Matrix chat bot — natural conversation via 3b model, `!why` and `!status` shortcuts |
| `jarvis.service` | systemd unit for the webhook/orchestrator (always-on, restarts on failure) |

## Stack

- **Orchestrator**: Python (Flask + requests) on Vivobook, systemd managed
- **Brain**: llama3.1:8b-instruct-q5_K_M via Ollama on MSI GE76 (RTX 2060)
- **Chat**: llama3.2:3b via Ollama on MSI — lighter model for conversational responses
- **Eyes**: Tapo C121 → Frigate NVR on NAS → Home Assistant
- **Hands**: Home Assistant REST API on Lenovo
- **Voice**: Matrix chat via Continuwuity on MSI + Element client

## Current capabilities

- Person detected → turn on living room light at context-appropriate brightness
- Occupancy cleared → turn off living room light
- Time-of-day brightness reasoning (morning 180 / day 255 / evening 150 / night 80)
- Decision audit trail in `decisions.jsonl`
- Real-time decision announcements in Matrix room
- Natural language chat with Jarvis from anywhere on Tailscale mesh
- `!why` to see recent decisions and Jarvis's reasoning
- `!status` to check current light states

## Setup

### Webhook + orchestrator (Vivobook)

```bash
cd ~/homelab_setup/projects/jarvis
pip install -r requirements.txt
export JARVIS_MATRIX_PASSWORD="your-matrix-bot-password"
python webhook.py
```

Or via systemd:
```bash
sudo cp jarvis.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jarvis
sudo systemctl start jarvis
```

### Matrix bot (Vivobook)

```bash
pip install matrix-nio --break-system-packages
export JARVIS_MATRIX_PASSWORD="your-matrix-bot-password"
python jarvis_bot.py
```

Runs as `jarvis-bot.service` alongside the main Jarvis service.

### HA automations required

Two automations in Home Assistant fire REST commands to the Vivobook:

- **Jarvis Person Detected**: Tapo C121 occupancy → detected → POST to Vivobook :5050/webhook with `{"event": "person_detected"}`
- **Jarvis Occupancy Cleared**: Tapo C121 occupancy → off → POST to Vivobook :5050/webhook with `{"event": "occupancy_cleared"}`

### Matrix server (MSI)

Continuwuity (Matrix homeserver) runs as a Docker container on the MSI:
```bash
cd ~/conduwuit
docker compose up -d
```
Accessible at `http://[MSI_TAILSCALE_IP]:6167`. Element client connects over Tailscale.

## Gotchas

- Ollama on the MSI must be listening on 0.0.0.0:11434, not localhost
- The 8b model runs at 100% GPU utilization during inference — don't stack 
  chat requests while Frigate events are being processed (that's why chat uses the 3b)
- HA long-lived access tokens don't expire for years but do need manual creation 
  in HA UI under Profile → Security
- Matrix room must have encryption OFF — the bot uses `matrix-nio` without 
  E2E support, encrypted messages show up as `MegolmEvent` and can't be read
- Jarvis's JSON parsing is fragile — if Ollama returns markdown or extra text 
  around the JSON, the decision fails silently. The prompt engineering matters

## Planned

- [ ] Lab light automation via hallway motion detection
- [ ] Frigate snapshot → multimodal LLM visual reasoning
- [ ] Halocode voice interface with LED feedback
- [ ] Coral TPU for Frigate detection upgrade
- [ ] 27B model on tower for heavy reasoning tasks
- [ ] Human-in-the-loop approval for high-impact actions via Matrix

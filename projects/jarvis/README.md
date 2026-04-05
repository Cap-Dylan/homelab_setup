# jarvis

Fully local agentic smart home system. Listens for events from Frigate NVR,
reasons about them using a local LLM, executes actions autonomously, and
responds to natural language commands via a self-hosted Matrix chat server.
No cloud, no subscriptions, no data leaving the network.

## How it works

Two input paths, one brain:

**Automated** — Frigate detects occupancy → HA automation fires REST command →
Jarvis webhook receives event → Ollama 8b reasons about state + time of day →
structured JSON decision → HA REST API executes action → decision logged

**Conversational** — You send a message in Element → Matrix bot receives it →
Ollama 8b reasons about intent (chat vs. command) → executes actions if needed →
responds naturally → decision logged

Both paths hit the same model, share the same decision log, and execute through
the same HA REST API. Everything converges.

## Files

| File | Role |
|------|------|
| `webhook.py` | Flask server on :5050 — receives events from HA REST commands |
| `jarvis.py` | Automated orchestrator — fetches HA state, prompts Ollama, parses JSON decision, calls HA service |
| `jarvis_bot.py` | Matrix chat interface — unified 8b brain handles conversation, commands, and reasoning |
| `ha_client.py` | Home Assistant REST API wrapper — `get_state`, `call_service` with brightness support |
| `ollama_client.py` | Ollama REST API wrapper — targets MSI on :11434 |
| `decision_log.py` | Writes every decision to `decisions.jsonl` — event, reasoning, action, timestamp |
| `matrix_notify.py` | Posts automated decisions to the Jarvis Matrix room in real time |
| `jarvis.service` | systemd unit for the webhook/orchestrator (always-on, restarts on failure) |

## Stack

- **Brain**: llama3.1:8b-instruct-q5_K_M via Ollama on MSI GE76 (RTX 2060, 32GB RAM)
- **Orchestrator**: Python (Flask + requests) on Vivobook, systemd managed
- **Chat**: Continuwuity (Matrix homeserver) on MSI + Element client over Tailscale
- **Eyes**: Tapo C121 → Frigate NVR on NAS → Home Assistant
- **Hands**: Home Assistant REST API on Lenovo

## Current capabilities

- Person detected → turn on living room light at context-appropriate brightness
- Occupancy cleared → turn off living room light
- Time-of-day brightness reasoning (morning 180 / day 255 / evening 150 / night 80)
- Natural language commands from Element ("turn on the lab light to an appropriate brightness")
- Direct HA control from chat — the 8b decides intent and executes actions through the same API
- Conversational reasoning about past decisions ("why did you turn on the light?") — explains its actual thinking, not just a log dump
- Decision audit trail in `decisions.jsonl` covering both automated and chat-triggered actions
- Conversation memory within a session so Jarvis has context across messages
- `!status` for quick light state check without LLM inference

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

### Matrix server (MSI)

Continuwuity (Matrix homeserver) runs as a Docker container on the MSI:
```bash
cd ~/conduwuit
docker compose up -d
```
Accessible at `http://[MSI_TAILSCALE_IP]:6167`. Element client connects over Tailscale.
Registration disabled after initial account creation.

### HA automations required

Two automations in Home Assistant fire REST commands to the Vivobook:

- **Jarvis Person Detected**: Tapo C121 occupancy → detected → POST to Vivobook :5050/webhook with `{"event": "person_detected"}`
- **Jarvis Occupancy Cleared**: Tapo C121 occupancy → off → POST to Vivobook :5050/webhook with `{"event": "occupancy_cleared"}`

## Architecture

The 8b model handles everything — no separate models for different tasks. When a chat
message comes in, the model gets the current HA state, the decision log, conversation
history, and the user's message. It returns a JSON response with a conversational reply
and an optional list of actions to execute. If JSON parsing fails, the raw output is
treated as conversation. This keeps the system simple — one brain, one decision log,
one execution path.

Chat-triggered actions get logged with `event: chat_command` so they show up in the
same timeline as Frigate-triggered decisions. When you ask "why did you do that?", the
model has the full log as context and can reason about its own behavior conversationally.

## Gotchas

- Ollama on the MSI must be listening on 0.0.0.0:11434, not localhost
- The 8b model runs at +75% GPU utilization during inference — requests queue up
  if Frigate and chat fire simultaneously, but the MSI handles it fine (78.89% VRAM, 0.6% CPU idle, 7.8% RAM)
- HA long-lived access tokens don't expire for years but need manual creation
  in HA UI under Profile → Security
- Matrix room must have encryption OFF — the bot uses `matrix-nio` without
  E2E support, encrypted messages show up as `MegolmEvent` and can't be read
- The LLM's JSON output is inherently fragile — if it returns markdown or extra text
  around the JSON, the bot falls back to treating the raw output as conversation
  instead of crashing. Prompt engineering matters




"""
jarvis_bot.py — Jarvis Matrix Chat Interface (v3 — Unified 8b Brain)

One model handles everything: conversation, commands, and reasoning.
You talk naturally, Jarvis decides if it needs to act or just respond.

"turn off the living room light" → executes it and confirms
"why did you turn on the light at 8pm?" → reasons about its decision log
"what's up?" → just chats

Shortcuts still work:
    !status — quick light states (no LLM needed)
    !help   — show available commands

Setup:
    1. export MATRIX_PASSWORd
    2. python3 jarvis_bot.py
"""

import os
import sys
import json
import asyncio
import requests
from datetime import datetime
from nio import AsyncClient, LoginResponse, RoomMessageText

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MATRIX_HOMESERVER = os.environ.get("MATRIX_HOMESERVER", "http://100.77.80.94:6167")
MATRIX_USER = os.environ.get("MATRIX_USER", "@jarvis:100.77.80.94")
MATRIX_PASSWORD = os.environ.get("MATRIX_PASSWORD", "")
JARVIS_ROOM_ID = os.environ.get("MATRIX_ROOM_ID", "!3toinz8WHv4l0hMrHV:100.77.80.94")

# Ollama on the MSI — one model for everything
OLLAMA_HOST = os.environ.get("OLLAMA_URL", "http://100.77.80.94:11434")
JARVIS_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b-instruct-q5_K_M")

# Home Assistant
HA_HOST = os.environ.get("HA_URL", "http://192.168.0.59:8123")
HA_TOKEN = os.environ["HA_TOKEN"]

HA_HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

# Entities Jarvis knows about and can control
KNOWN_ENTITIES = {
    "living room light": "light.wiz_rgbww_tunable_a480ec",
    "lab light": "light.wiz_rgbww_tunable_225a0a",
}

DECISIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "decisions.jsonl")

# Conversation memory (resets on restart)
conversation_history = []
MAX_HISTORY = 10


# ---------------------------------------------------------------------------
# Home Assistant helpers
# ---------------------------------------------------------------------------

def get_all_light_states():
    """Get current state of all tracked lights. Returns a readable string."""
    summary = ""
    for name, entity_id in KNOWN_ENTITIES.items():
        try:
            resp = requests.get(
                f"{HA_HOST}/api/states/{entity_id}",
                headers=HA_HEADERS,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            state = data.get("state", "unknown")
            brightness_raw = data.get("attributes", {}).get("brightness")
            if brightness_raw is not None:
                brightness_pct = round((brightness_raw / 255) * 100)
                summary += f"- {name}: {state} (brightness: {brightness_pct}%)\n"
            else:
                summary += f"- {name}: {state}\n"
        except Exception as e:
            summary += f"- {name}: error ({e})\n"
    return summary


def execute_action(action):
    """
    Execute a single action dict from the LLM.
    Expected format: {"action": "turn_on"/"turn_off", "entity": "living room light", "brightness": 150}
    Returns a string describing what happened.
    """
    action_type = action.get("action", "").lower()
    entity_name = action.get("entity", "").lower()
    brightness = action.get("brightness")

    # Resolve friendly name to entity_id
    entity_id = KNOWN_ENTITIES.get(entity_name)
    if not entity_id:
        return f"I don't know how to control '{entity_name}'. I can control: {', '.join(KNOWN_ENTITIES.keys())}"

    try:
        if action_type == "turn_on":
            payload = {"entity_id": entity_id}
            if brightness is not None:
                payload["brightness"] = int(brightness)
            resp = requests.post(
                f"{HA_HOST}/api/services/light/turn_on",
                headers=HA_HEADERS,
                json=payload,
                timeout=10,
            )
            resp.raise_for_status()
            bri_str = f" at {brightness}/255" if brightness else ""
            return f"Turned on {entity_name}{bri_str}"

        elif action_type == "turn_off":
            resp = requests.post(
                f"{HA_HOST}/api/services/light/turn_off",
                headers=HA_HEADERS,
                json={"entity_id": entity_id},
                timeout=10,
            )
            resp.raise_for_status()
            return f"Turned off {entity_name}"

        else:
            return f"Unknown action type: {action_type}"

    except Exception as e:
        return f"Failed to execute {action_type} on {entity_name}: {e}"


# ---------------------------------------------------------------------------
# Decision log
# ---------------------------------------------------------------------------

def get_recent_decisions(n=10):
    """Read the last N decisions from the JSONL log."""
    if not os.path.exists(DECISIONS_FILE):
        return []

    with open(DECISIONS_FILE, "r") as f:
        lines = f.readlines()

    decisions = []
    for line in lines[-n:]:
        line = line.strip()
        if not line:
            continue
        try:
            decisions.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return decisions


def log_decision(event, reasoning, action, details=None):
    """Log a decision from a chat command."""
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": event,
        "reasoning": reasoning,
        "action": action,
    }
    if details:
        entry["details"] = details

    with open(DECISIONS_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# Core: ask the 8b to reason and (optionally) act
# ---------------------------------------------------------------------------

def ask_jarvis(user_message):
    """
    Send a message to the 8b model with full context.
    Returns (response_text, actions_executed).
    """
    global conversation_history

    # Gather context
    light_states = get_all_light_states()
    hour = datetime.now().hour
    time_str = datetime.now().strftime("%I:%M %p")

    # Decision log context
    decisions = get_recent_decisions(10)
    decision_context = ""
    if decisions:
        decision_context = "My recent decision log (newest last):\n"
        for d in decisions:
            decision_context += (
                f"  [{d.get('timestamp')}] event={d.get('event')} "
                f"action={d.get('action')} reason=\"{d.get('reasoning')}\"\n"
            )

    # Conversation history
    history_str = ""
    if conversation_history:
        for entry in conversation_history[-MAX_HISTORY:]:
            history_str += f"User: {entry['user']}\nJarvis: {entry['jarvis']}\n"

    prompt = f"""You are Jarvis, an AI smart home assistant running fully locally on a private homelab.
You have direct control over the smart home via Home Assistant.

CURRENT STATE:
- Time: {time_str} (hour {hour})
- Lights:
{light_states}

{decision_context}

AVAILABLE ACTIONS:
You can control these devices:
- "living room light" — turn_on (with brightness 0-255) or turn_off
- "lab light" — turn_on (with brightness 0-255) or turn_off

Brightness guide for context:
- Morning (6-9): 180
- Daytime (9-17): 255
- Evening (17-21): 150
- Night (21-6): 80

RESPONSE FORMAT:
Always respond with a SINGLE JSON object. Nothing else — no markdown, no backticks, no multiple objects, just ONE JSON object.

If the user is asking you to DO something (control a light, change brightness, etc.):
{{"response": "your conversational response", "actions": [{{"action": "turn_on" or "turn_off", "entity": "living room light" or "lab light", "brightness": 0-255}}]}}

If the user is just chatting or asking a question (why did you do X, what's going on, etc.):
{{"response": "your conversational response"}}

CRITICAL: Put "response" and "actions" in the SAME JSON object. Never split them into separate objects.

CONVERSATION RULES:
- Be conversational and natural, not robotic
- When asked WHY you did something, look at your decision log and explain your actual reasoning in your own words — don't just list log entries
- When asked to control something, do it and confirm naturally
- If you're not sure what the user wants, ask for clarification
- Keep responses concise but thoughtful

{history_str}User: {user_message}
Jarvis:"""

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": JARVIS_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )
        resp.raise_for_status()
        raw_response = resp.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return ("Can't reach Ollama on the MSI. Is it running?", [])
    except requests.exceptions.Timeout:
        return ("Ollama timed out — the model might be loading.", [])
    except Exception as e:
        return (f"Error talking to Ollama: {e}", [])

    # Parse the JSON response
    try:
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        parsed = json.loads(cleaned)
        response_text = parsed.get("response", raw_response)
        actions = parsed.get("actions", [])
    except json.JSONDecodeError:
        # Fallback: try to find multiple JSON objects the LLM split apart
        response_text = raw_response
        actions = []
        try:
            for chunk in raw_response.replace("}\n{", "}|||{").replace("} {", "}|||{").split("|||"):
                part = json.loads(chunk.strip())
                if "response" in part:
                    response_text = part["response"]
                if "actions" in part:
                    actions = part["actions"]
        except (json.JSONDecodeError, Exception):
            pass

    # Execute any actions
    action_results = []
    for action in actions:
        result = execute_action(action)
        action_results.append(result)

        # Log the action
        log_decision(
            event="chat_command",
            reasoning=response_text,
            action=f"{action.get('action')} {action.get('entity', 'unknown')}",
            details={"brightness": action.get("brightness"), "source": "matrix_chat"},
        )

    # Store in conversation history
    conversation_history.append({
        "user": user_message,
        "jarvis": response_text,
    })
    if len(conversation_history) > MAX_HISTORY:
        conversation_history = conversation_history[-MAX_HISTORY:]

    return (response_text, action_results)


# ---------------------------------------------------------------------------
# Quick status (no LLM needed)
# ---------------------------------------------------------------------------

def handle_status():
    """Direct HA query, no inference required."""
    states = get_all_light_states()
    return f"Smart Home Status:\n\n{states}"


# ---------------------------------------------------------------------------
# Matrix bot
# ---------------------------------------------------------------------------

async def main():
    if not MATRIX_PASSWORD:
        print("ERROR: Set JARVIS_MATRIX_PASSWORD environment variable")
        sys.exit(1)

    client = AsyncClient(MATRIX_HOMESERVER, MATRIX_USER)

    print(f"Logging in as {MATRIX_USER}...")
    login_response = await client.login(MATRIX_PASSWORD)

    if not isinstance(login_response, LoginResponse):
        print(f"Login failed: {login_response}")
        sys.exit(1)

    print(f"Logged in. Device ID: {login_response.device_id}")

    # Initial sync — skip old messages
    print("Initial sync...")
    await client.sync(timeout=10000)
    print("Listening for messages...")

    async def message_callback(room, event):
        """Handle every message in the Jarvis room."""
        if room.room_id != JARVIS_ROOM_ID:
            return
        if event.sender == MATRIX_USER:
            return

        content = event.body.strip()
        lower = content.lower()

        # Quick shortcuts that don't need LLM
        if lower == "!help":
            response = (
                "Just talk to me — no commands needed.\n\n"
                "I can control the living room light and lab light.\n"
                "Ask me why I did something and I'll explain my reasoning.\n\n"
                "Shortcuts:\n"
                "  !status — quick light states\n"
                "  !help — this message"
            )
            await client.room_send(
                room_id=JARVIS_ROOM_ID,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": response},
            )
            return

        if lower.startswith("!status"):
            response = handle_status()
            await client.room_send(
                room_id=JARVIS_ROOM_ID,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": response},
            )
            return

        # Everything else goes to the 8b
        response_text, action_results = await asyncio.to_thread(ask_jarvis, content)

        # Build the message to send back
        message = response_text
        if action_results:
            message += "\n\n" + "\n".join(f"[executed] {r}" for r in action_results)

        if len(message) > 4000:
            message = message[:4000] + "\n\n... (truncated)"

        await client.room_send(
            room_id=JARVIS_ROOM_ID,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": message},
        )

    client.add_event_callback(message_callback, RoomMessageText)
    await client.sync_forever(timeout=30000)


if __name__ == "__main__":
    asyncio.run(main())

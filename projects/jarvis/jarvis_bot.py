"""
jarvis_bot.py — Jarvis Matrix Chat Interface

A Matrix bot that lets you talk to Jarvis from Element.
Runs on the Vivobook alongside jarvis.py.

Commands:
    !ask <question>   Chat with Jarvis (sends to Ollama on MSI)
    !why              Show recent Jarvis decisions and reasoning
    !why <number>     Show last N decisions (default 5, max 20)
    !status           Check current smart home light states
    !help             Show available commands

Setup:
    1. Set environment variable: export JARVIS_MATRIX_PASSWORD="your-password"
    2. Run: python3 jarvis_bot.py

All AI reasoning stays local — Matrix messages stay on your Conduwuit server.
"""

import os
import sys
import json
import asyncio
import requests
from nio import AsyncClient, RoomMessageText, LoginResponse

# ---------------------------------------------------------------------------
# Configuration — all your service addresses
# ---------------------------------------------------------------------------

# Conduwuit on the MSI (Matrix server)
MATRIX_HOMESERVER = "http://100.77.80.94:6167"
MATRIX_USER = "@jarvis:100.77.80.94"
MATRIX_PASSWORD = os.environ.get("JARVIS_MATRIX_PASSWORD", "")

# The Jarvis chat room you created in Element
JARVIS_ROOM_ID = "!3toinz8WHv4l0hMrHV:100.77.80.94"

# Ollama on the MSI (Jarvis brain)
OLLAMA_HOST = "http://100.77.80.94:11434"
JARVIS_MODEL = "llama3.1:8b-instruct-q5_K_M"

# Home Assistant on the Lenovo (same LAN)
HA_HOST = "http://192.168.0.59:8123"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI3NGU0MzZhNGI0YzA0OWFjYTAyN2NlNDBmNjQwMjFjNyIsImlhdCI6MTc3NTI4MTQwMCwiZXhwIjoyMDkwNjQxNDAwfQ.UA1LqJLGOcXd9RT7329ahnAKEkYsctdN53muBg9Rn-k"

# Lights to show in !status
TRACKED_LIGHTS = [
    "light.wiz_rgbww_tunable_a480ec",  # Living room (Jarvis-controlled)
    "light.wiz_rgbww_tunable_225a0a",  # Lab
]

# Path to the decision log (same folder as jarvis.py)
DECISIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "decisions.jsonl")


# ---------------------------------------------------------------------------
# Helper functions — talk to your local services
# ---------------------------------------------------------------------------

def ask_ollama(prompt):
    """Send a prompt to Ollama on the MSI and get a response."""
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
        return resp.json().get("response", "No response from Ollama.")
    except requests.exceptions.ConnectionError:
        return "Can't reach Ollama on the MSI. Is it running?"
    except requests.exceptions.Timeout:
        return "Ollama timed out — the model might be loading."
    except Exception as e:
        return f"Error talking to Ollama: {e}"


def get_recent_decisions(n=5):
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


def get_ha_entity_state(entity_id):
    """Get current state of a Home Assistant entity."""
    try:
        resp = requests.get(
            f"{HA_HOST}/api/states/{entity_id}",
            headers={
                "Authorization": f"Bearer {HA_TOKEN}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"state": "error", "error": str(e)}


# ---------------------------------------------------------------------------
# Command handlers — each one processes a command and returns a string
# ---------------------------------------------------------------------------

def handle_help():
    """Return the help text."""
    return (
        "Jarvis Commands:\n\n"
        "!ask <question> — Chat with Jarvis (local Ollama)\n"
        "!why — See recent decisions + reasoning\n"
        "!why <number> — Show last N decisions (default 5)\n"
        "!status — Check current light states\n"
        "!help — Show this message"
    )


def handle_why(args):
    """Return recent Jarvis decisions."""
    # Parse optional count
    count = 5
    if args:
        try:
            count = min(int(args), 20)
        except ValueError:
            pass

    decisions = get_recent_decisions(count)

    if not decisions:
        return "No decisions logged yet. Jarvis hasn't acted since logging was enabled."

    response = f"Last {len(decisions)} decision(s):\n\n"
    for d in decisions:
        timestamp = d.get("timestamp", "unknown")
        event = d.get("event", "unknown")
        reasoning = d.get("reasoning", "no reasoning recorded")
        action = d.get("action", "no action")
        details = d.get("details", {})

        brightness = details.get("brightness", "N/A") if details else "N/A"

        response += (
            f"[{timestamp}] {event}\n"
            f"  Why: {reasoning}\n"
            f"  Did: {action} (brightness: {brightness})\n\n"
        )

    return response.strip()


def handle_status():
    """Return current light states from HA."""
    response = "Smart Home Status:\n\n"

    for entity_id in TRACKED_LIGHTS:
        state_data = get_ha_entity_state(entity_id)

        if "error" in state_data:
            response += f"  {entity_id}: Error — {state_data['error']}\n"
            continue

        friendly_name = state_data.get("attributes", {}).get("friendly_name", entity_id)
        state = state_data.get("state", "unknown")
        brightness_raw = state_data.get("attributes", {}).get("brightness")

        # HA brightness is 0-255, convert to percentage
        if brightness_raw is not None:
            brightness_pct = round((brightness_raw / 255) * 100)
            brightness_str = f"{brightness_pct}%"
        else:
            brightness_str = "N/A"

        indicator = "ON" if state == "on" else "OFF"
        response += f"  [{indicator}] {friendly_name} — brightness: {brightness_str}\n"

    return response.strip()


def handle_ask(question):
    """Send a question to Ollama with recent decision context."""
    # Include recent decisions so Jarvis can reference its own history
    decisions = get_recent_decisions(3)
    context = ""
    if decisions:
        context = "Here are my recent smart home decisions:\n"
        for d in decisions:
            context += (
                f"- {d.get('timestamp')}: {d.get('event')} -> "
                f"{d.get('action')} (reason: {d.get('reasoning')})\n"
            )
        context += "\n"

    prompt = (
        "You are Jarvis, a local smart home AI assistant running on a private homelab. "
        "You control lights based on occupancy and time of day. "
        "You run fully locally with no cloud dependencies. "
        "Answer the user's question conversationally and concisely.\n\n"
        f"{context}"
        f"User: {question}\n"
        "Jarvis:"
    )

    return ask_ollama(prompt)


# ---------------------------------------------------------------------------
# Matrix bot — connects to Conduwuit and listens for messages
# ---------------------------------------------------------------------------

async def main():
    """Main bot loop — connect, sync, and handle messages."""

    if not MATRIX_PASSWORD:
        print("ERROR: Set JARVIS_MATRIX_PASSWORD environment variable")
        print("  export JARVIS_MATRIX_PASSWORD='your-password-here'")
        sys.exit(1)

    # Create the Matrix client
    client = AsyncClient(MATRIX_HOMESERVER, MATRIX_USER)

    # Log in
    print(f"Logging in as {MATRIX_USER}...")
    login_response = await client.login(MATRIX_PASSWORD)

    if not isinstance(login_response, LoginResponse):
        print(f"Login failed: {login_response}")
        sys.exit(1)

    print(f"Logged in successfully. Device ID: {login_response.device_id}")

    # Do an initial sync so we don't respond to old messages
    print("Running initial sync (ignoring old messages)...")
    await client.sync(timeout=10000)
    print("Initial sync done. Listening for new messages...")

    # Register the message handler AFTER initial sync
    # This way we only respond to messages that arrive from now on
    async def message_callback(room, event):
        """Called every time a message appears in a room we're in."""

        # Only respond in the Jarvis room
        if room.room_id != JARVIS_ROOM_ID:
            return

        # Don't respond to our own messages
        if event.sender == MATRIX_USER:
            return

        content = event.body.strip()

        # Route to the right handler
        if content.lower() == "!help":
            response = handle_help()

        elif content.lower().startswith("!why"):
            args = content[4:].strip()
            response = handle_why(args)

        elif content.lower().startswith("!status"):
            response = handle_status()

        elif content.lower().startswith("!ask "):
            question = content[5:].strip()
            if not question:
                response = "Usage: !ask <your question>"
            else:
                # Run the Ollama call in a thread so we don't block
                response = await asyncio.to_thread(handle_ask, question)

        else:
            # If it's not a command, ignore it (or treat everything as !ask)
            # Uncomment the next line if you want Jarvis to respond to ALL messages:
            # response = await asyncio.to_thread(handle_ask, content)
            return

        # Send the response back to the room
        # Truncate if too long (Matrix has a ~65KB limit but let's keep it readable)
        if len(response) > 4000:
            response = response[:4000] + "\n\n... (truncated)"

        await client.room_send(
            room_id=JARVIS_ROOM_ID,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": response,
            },
        )

    # Register the callback
    client.add_event_callback(message_callback, RoomMessageText)

    # Sync forever — this keeps the bot running and listening
    await client.sync_forever(timeout=30000)


if __name__ == "__main__":
    asyncio.run(main())

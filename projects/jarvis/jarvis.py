import json
from datetime import datetime
from ha_client import get_state, call_service
from ollama_client import ask_ollama

def run_jarvis(event_data=None):
    camera_state = get_state("camera.tapo_c121")
    light_state = get_state("light.wiz_rgbww_tunable_a480ec")
    event = event_data.get("event", "unknown") if event_data else "unknown"
    hour = datetime.now().hour

    prompt = f"""You are a smart home assistant controlling a living room.

Current state:
- Camera occupancy: {camera_state}
- Living room light: {light_state}
- Event that triggered this: {event}
- Current hour (24h): {hour}

Available actions:
- turn_on the living room light
- turn_off the living room light
- do_nothing

Rules:
- If event is "person_detected" and light is off, turn it on
- if event is "occupancy_cleared", always turn the light off
- If event is "person_detected" and light is on, do_nothing

Brightness guide:
- Morning (6-9): 180
- Daytime (9-17): 255
- Evening (17-21): 150
- Night (21-6): 80

Respond with ONLY a JSON object in this exact format, no other text:
{{"action": "turn_on" or "turn_off" or "do_nothing", "brightness": 0-255, "reason": "one sentence explanation"}}"""

    response = ask_ollama(prompt)

    try:
        decision = json.loads(response)
        print(f"Action: {decision['action']}")
        print(f"Brightness: {decision.get('brightness')}")
        print(f"Reason: {decision['reason']}")

        if decision['action'] == "turn_on":
            call_service("light", "turn_on", "light.wiz_rgbww_tunable_a480ec", brightness=decision.get("brightness"))
        elif decision['action'] == "turn_off":
            call_service("light", "turn_off", "light.wiz_rgbww_tunable_a480ec")
        else:
            print("No action taken.")

    except json.JSONDecodeError:
        print(f"Jarvis returned unexpected format: {response}")

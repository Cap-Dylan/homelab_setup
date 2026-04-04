import json
from ha_client import get_state, call_service
from ollama_client import ask_ollama

def run_jarvis():
    camera_state = get_state("camera.tapo_c121")
    light_state = get_state("light.wiz_rgbww_tunable_a480ec")

    prompt = f"""You are a smart home assistant controlling a living room.

Current state:
- Camera: {camera_state}
- Living room light: {light_state}

Available actions:
- turn_on the living room light
- turn_off the living room light
- do_nothing

Respond with ONLY a JSON object in this exact format, no other text:
{{"action": "turn_on" or "turn_off" or "do_nothing", "reason": "one sentence explanation"}}"""

    response = ask_ollama(prompt)
    
    try:
        decision = json.loads(response)
        print(f"Action: {decision['action']}")
        print(f"Reason: {decision['reason']}")

        if decision['action'] == "turn_on":
            call_service("light", "turn_on", "light.wiz_rgbww_tunable_a480ec")
        elif decision['action'] == "turn_off":
            call_service("light", "turn_off", "light.wiz_rgbww_tunable_a480ec")
        else:
            print("No action taken.")

    except json.JSONDecodeError:
        print(f"Jarvis returned unexpected format: {response}")

if __name__ == "__main__":
    run_jarvis()

from decision_log import log_decision
import json
from datetime import datetime
from ha_client import get_state, call_service
from ollama_client import ask_ollama

def get_brightness(hour):
    """Deterministic brightness lookup — no LLM needed."""
    if 6 <= hour < 9:
        return 180
    elif 9 <= hour < 17:
        return 255
    elif 17 <= hour < 21:
        return 150
    else:
        return 80

def get_color_temp(hour, weather):
    """Ask Jarvis only for color temperature reasoning."""
    prompt = f"""You control a living room light's color temperature.
Current hour (24h): {hour}
Current weather: {weather}

Color temperature guide (Kelvin, range 2000-6500):
- Clear/sunny daytime: 4000-5000 Kelvin (cool white)
- Overcast/rainy: 2700-3200 Kelvin (warm white)
- Evening: 2500-3000 Kelvin (warm)
- Night/clear-night: 2200-2700 Kelvin (very warm)

Respond with ONLY a JSON object, no other text:
{{"color_temp_kelvin": 2000-6500, "reason": "one sentence explanation"}}"""

    response = ask_ollama(prompt)
    try:
        result = json.loads(response)
        return (
            result.get("color_temp_kelvin", 3000),
            result.get("reason", "")
        )
    except json.JSONDecodeError:
        return 3000, "LLM response failed, using default"

def run_jarvis(event_data=None):
    light_state = get_state("light.wiz_rgbww_tunable_a480ec")
    weather = get_state("weather.forecast_home")
    event = event_data.get("event", "unknown") if event_data else "unknown"
    hour = datetime.now().hour

    # --- Hardcoded decision logic ---
    light_is_on = light_state == "on"

    if event == "occupancy_cleared":
        action = "turn_off"
        brightness = None
        color_temp = None
        reason = "Occupancy cleared — turning off"

    elif event == "person_detected" and not light_is_on:
        action = "turn_on"
        brightness = get_brightness(hour)
        color_temp, reason = get_color_temp(hour, weather)

    elif event == "person_detected" and light_is_on:
        action = "do_nothing"
        brightness = None
        color_temp = None
        reason = "Person detected, light already on"

    else:
        action = "do_nothing"
        brightness = None
        color_temp = None
        reason = f"Unhandled event: {event}"

    # --- Execute and log ---
    print(f"Action: {action}")
    print(f"Brightness: {brightness}")
    print(f"Color temp: {color_temp}")
    print(f"Weather: {weather}")
    print(f"Reason: {reason}")

    log_decision(
        event=event,
        reasoning=reason,
        action=action,
        details={
            "brightness": brightness,
            "color_temp_kelvin": color_temp,
            "weather": weather
        }
    )

    if action == "turn_on":
        call_service("light", "turn_on",
                     "light.wiz_rgbww_tunable_a480ec",
                     brightness=brightness,
                     color_temp_kelvin=color_temp)
    elif action == "turn_off":
        call_service("light", "turn_off",
                     "light.wiz_rgbww_tunable_a480ec")
    else:
        print("No action taken.")

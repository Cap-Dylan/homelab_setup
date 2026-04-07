from decision_log import log_decision
import json
import threading
from datetime import datetime
from ha_client import get_state, call_service
from ollama_client import ask_ollama

# --- State (persists while Flask is running) ---
last_turn_on_time = None
pending_off_timer = None
COOLDOWN_SECONDS = 120
OFF_DELAY_SECONDS = 120

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

def delayed_turn_off():
    """Runs after OFF_DELAY_SECONDS if not cancelled."""
    global pending_off_timer
    pending_off_timer = None

    light_state = get_state("light.wiz_rgbww_tunable_a480ec")
    weather = get_state("weather.forecast_home")

    if light_state == "on":
        call_service("light", "turn_off",
                     "light.wiz_rgbww_tunable_a480ec")
        log_decision(
            event="occupancy_cleared",
            reasoning=f"Occupancy cleared for {OFF_DELAY_SECONDS}s — turning off",
            action="turn_off",
            details={"brightness": None,
                     "color_temp_kelvin": None,
                     "weather": weather}
        )
        print(f"Delayed turn_off executed after {OFF_DELAY_SECONDS}s")
    else:
        print("Delayed turn_off fired but light already off")

def run_jarvis(event_data=None):
    global last_turn_on_time, pending_off_timer

    event = event_data.get("event", "unknown") if event_data else "unknown"

    if event == "person_detected":
        # Cancel any pending turn-off
        if pending_off_timer:
            pending_off_timer.cancel()
            pending_off_timer = None
            print("Pending turn-off cancelled — person detected")

        # Cooldown check
        if last_turn_on_time:
            elapsed = (datetime.now() - last_turn_on_time).total_seconds()
            if elapsed < COOLDOWN_SECONDS:
                print(f"Cooldown active, skipping ({elapsed:.0f}s elapsed)")
                log_decision(
                    event=event,
                    reasoning="Cooldown active, skipping",
                    action="skip",
                    details={"cooldown_seconds": COOLDOWN_SECONDS}
                )
                return

        light_state = get_state("light.wiz_rgbww_tunable_a480ec")
        weather = get_state("weather.forecast_home")
        hour = datetime.now().hour
        light_is_on = light_state == "on"

        if not light_is_on:
            action = "turn_on"
            brightness = get_brightness(hour)
            color_temp, reason = get_color_temp(hour, weather)

            call_service("light", "turn_on",
                         "light.wiz_rgbww_tunable_a480ec",
                         brightness=brightness,
                         color_temp_kelvin=color_temp)
            last_turn_on_time = datetime.now()
        else:
            action = "do_nothing"
            brightness = None
            color_temp = None
            reason = "Person detected, light already on"

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
        print(f"Action: {action} | Brightness: {brightness} | Color temp: {color_temp}")

    elif event == "occupancy_cleared":
        # Schedule turn-off, don't act immediately
        if pending_off_timer:
            pending_off_timer.cancel()

        pending_off_timer = threading.Timer(OFF_DELAY_SECONDS, delayed_turn_off)
        pending_off_timer.start()

        print(f"Occupancy cleared — turn-off scheduled in {OFF_DELAY_SECONDS}s")
        log_decision(
            event=event,
            reasoning=f"Occupancy cleared — turn-off scheduled in {OFF_DELAY_SECONDS}s",
            action="scheduled_off",
            details={"delay_seconds": OFF_DELAY_SECONDS}
        )

    else:
        print(f"Unhandled event: {event}")

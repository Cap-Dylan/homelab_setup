import os
import requests

HA_URL = os.environ.get("HA_URL", "http://localhost:8123")
TOKEN = os.environ["HA_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def get_state(entity_id):
    response = requests.get(f"{HA_URL}/api/states/{entity_id}", headers=HEADERS)
    data = response.json()
    return data["state"]


def call_service(domain, service, entity_id, brightness=None, color_temp_kelvin=None):
    payload = {"entity_id": entity_id}
    if brightness is not None:
        payload["brightness"] = brightness
    if color_temp_kelvin is not None:
        payload["color_temp_kelvin"] = color_temp_kelvin
    response = requests.post(
        f"{HA_URL}/api/services/{domain}/{service}",
        headers=HEADERS,
        json=payload
    )
    return response.status_code


if __name__ == "__main__":
    state = get_state("camera.tapo_c121")
    print(f"Camera state: {state}")
    status = call_service("light", "turn_on", "light.wiz_rgbww_tunable_a480ec")
    print(f"Service call status: {status}")

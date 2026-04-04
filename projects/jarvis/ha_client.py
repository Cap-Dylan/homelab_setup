import requests

HA_URL = "http://192.168.0.59:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI3NGU0MzZhNGI0YzA0OWFjYTAyN2NlNDBmNjQwMjFjNyIsImlhdCI6MTc3NTI4MTQwMCwiZXhwIjoyMDkwNjQxNDAwfQ.UA1LqJLGOcXd9RT7329ahnAKEkYsctdN53muBg9Rn-k"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def get_state(entity_id):
    response = requests.get(f"{HA_URL}/api/states/{entity_id}", headers=HEADERS)
    data = response.json()
    return data["state"]

def call_service(domain, service, entity_id, brightness=None):
    payload = {"entity_id": entity_id}
    if brightness is not None:
        payload["brightness"] = brightness
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

from flask import Flask, request, jsonify
from jarvis import run_jarvis

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(f"Event received: {data}")
    run_jarvis(data)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)

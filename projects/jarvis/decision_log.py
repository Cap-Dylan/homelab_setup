"""
decision_log.py — Jarvis Decision Logger

Writes every Jarvis decision to a JSONL file.
The Matrix bot reads this file to answer "!why" questions.
"""

import json
import os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "decisions.jsonl")
MAX_ENTRIES = 500


def log_decision(event, reasoning, action, details=None):
    """Append one decision to the log file."""
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": event,
        "reasoning": reasoning,
        "action": action,
    }
    if details:
        entry["details"] = details

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    # Trim if log gets too long
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
        if len(lines) > MAX_ENTRIES:
            with open(LOG_FILE, "w") as f:
                f.writelines(lines[-MAX_ENTRIES:])


def get_recent_decisions(n=5):
    """Read the last N decisions from the log."""
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r") as f:
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

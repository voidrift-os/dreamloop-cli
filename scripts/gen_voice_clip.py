import json
import os
import requests
from pathlib import Path

VOICE_PAYLOAD_FILE = "voice_payload.json"
OUTPUT_MP3 = "voice/dreamloop_voice.mp3"
WEBHOOK_URL = "http://localhost:5678/webhook/generate-voice"


def run():
    """Generate voiceover using the local ElevenLabs webhook."""
    if not Path(VOICE_PAYLOAD_FILE).exists():
        raise FileNotFoundError(f"Missing {VOICE_PAYLOAD_FILE}")

    with open(VOICE_PAYLOAD_FILE, "r") as fh:
        payload = json.load(fh)

    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"[error] Voice generation failed: {exc}")
        raise

    os.makedirs(os.path.dirname(OUTPUT_MP3), exist_ok=True)
    with open(OUTPUT_MP3, "wb") as fh:
        fh.write(response.content)

    print(f"[+] Voice clip saved to {OUTPUT_MP3}")

if __name__ == "__main__":
    run()

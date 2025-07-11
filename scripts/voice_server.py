import os
import requests
from flask import Flask, request, jsonify

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
OUTPUT_DIR = "voice_outputs"

app = Flask(__name__)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_voice_clip(text: str, voice_id: str = VOICE_ID):
    """Generate an MP3 file from text using ElevenLabs."""
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.9,
        },
    }
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers=headers,
        json=payload,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Voice generation failed: {response.text}")
    filename = text[:32].replace(" ", "_").replace("/", "-") + ".mp3"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(response.content)
    print(f"[✓] Voice saved to {filepath}")
    return filepath


@app.route("/generate-voice", methods=["POST"])
def generate_voice():
    data = request.json or {}
    text = data.get("text")
    voice_id = data.get("voice_id", VOICE_ID)

    if not text:
        return jsonify({"error": "Missing 'text' field"}), 400

    print(f"[+] Generating voice for: {text}")

    try:
        filepath = create_voice_clip(text, voice_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Voice generated", "file": filepath})

if __name__ == "__main__":
    app.run(port=5678)

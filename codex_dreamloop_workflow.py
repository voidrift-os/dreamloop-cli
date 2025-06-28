# codex_dreamloop_workflow.py
import os
import json
import datetime
from pathlib import Path

# === ENVIRONMENT SETUP ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

# === INPUT MEMORY ===
MEMORY_FILE = "dreamloop_memory.md"

# === OUTPUT FILES ===
VOICE_PAYLOAD_FILE = "voice_payload.json"
SCENE_PROMPTS_FILE = "scene_prompts.json"
VIDEO_WORKFLOW_FILE = "video_workflow.yaml"

# === PARSE MEMORY ===
def parse_memory_file(path):
    with open(path, 'r') as f:
        content = f.read()

    title = content.splitlines()[0].replace("# ", "").strip()
    scenes = content.split("---")
    parsed_scenes = []
    for scene in scenes:
        if "Scene" in scene:
            lines = scene.strip().splitlines()
            prompt = next((l for l in lines if "Prompt:" in l), "").replace("Prompt:", "").strip()
            motion = next((l for l in lines if "Motion:" in l), "").replace("Motion:", "").strip()
            parsed_scenes.append({"prompt": prompt, "motion": motion})

    return title, parsed_scenes

# === GENERATE PAYLOADS ===
def generate_voice_payload(text):
    return {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.85
        }
    }

def generate_scene_prompts(scenes):
    return [
        {
            "image_prompt": s["prompt"],
            "motion_prompt": s["motion"]
        } for s in scenes
    ]

def generate_video_workflow(title, scenes):
    return {
        "title": title,
        "scene_count": len(scenes),
        "duration_sec": len(scenes) * 5,
        "assets": {
            "voiceover": VOICE_PAYLOAD_FILE,
            "scenes": SCENE_PROMPTS_FILE
        }
    }


# === MAIN EXECUTION ===
def run():
    if not Path(MEMORY_FILE).exists():
        raise FileNotFoundError("Missing dreamloop_memory.md file")

    title, scenes = parse_memory_file(MEMORY_FILE)
    full_script = "\n".join([s["prompt"] for s in scenes])

    # Write voice payload
    with open(VOICE_PAYLOAD_FILE, 'w') as f:
        json.dump(generate_voice_payload(full_script), f, indent=2)

    # Write scene prompts
    with open(SCENE_PROMPTS_FILE, 'w') as f:
        json.dump(generate_scene_prompts(scenes), f, indent=2)

    # Write workflow file
    with open(VIDEO_WORKFLOW_FILE, 'w') as f:
        json.dump(generate_video_workflow(title, scenes), f, indent=2)

    print(f"[+] Workflow created for: {title}")

if __name__ == "__main__":
    run()

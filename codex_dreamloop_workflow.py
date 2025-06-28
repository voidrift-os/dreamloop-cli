# codex_dreamloop_workflow.py
import os
import json
import subprocess
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


def write_yaml(data, path: str) -> None:
    """Write a minimal YAML representation to the given path."""
    def _to_yaml(obj, indent: int = 0) -> list[str]:
        space = " " * indent
        if isinstance(obj, dict):
            lines = []
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{space}{k}:")
                    lines.extend(_to_yaml(v, indent + 2))
                else:
                    val = json.dumps(v) if isinstance(v, str) else v
                    lines.append(f"{space}{k}: {val}")
            return lines
        elif isinstance(obj, list):
            lines = []
            for item in obj:
                if isinstance(item, (dict, list)):
                    lines.append(f"{space}-")
                    lines.extend(_to_yaml(item, indent + 2))
                else:
                    val = json.dumps(item) if isinstance(item, str) else item
                    lines.append(f"{space}- {val}")
            return lines
        else:
            return [f"{space}{obj}"]

    with open(path, "w") as fh:
        fh.write("\n".join(_to_yaml(data)))


def push_to_github(commit_msg="Auto-update Dreamloop workflow"):
    subprocess.run(["git", "add", VOICE_PAYLOAD_FILE, SCENE_PROMPTS_FILE, VIDEO_WORKFLOW_FILE], check=True)
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    subprocess.run(["git", "push"], check=True)


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
    write_yaml(generate_video_workflow(title, scenes), VIDEO_WORKFLOW_FILE)

    print(f"[+] Workflow created for: {title}")

if __name__ == "__main__":
    run()
    push_to_github("🌀 Auto-generated Dreamloop video workflow")

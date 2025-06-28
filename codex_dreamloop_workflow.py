import os
import json
import subprocess

MEMORY_FILE = "dreamloop_memory.md"

# === OUTPUT FILES ===
VOICE_PAYLOAD_FILE = "voice_payload.json"
SCENE_PROMPTS_FILE = "scene_prompts.json"
VIDEO_WORKFLOW_FILE = "video_workflow.yaml"

# === PARSE MEMORY ===
def parse_memory_file(path):
    with open(path, "r") as f:
        lines = f.readlines()

    title = lines[0].strip()
    scenes = []
    current_scene = {"image_prompt": "", "motion_prompt": ""}
    mode = None

    for line in lines[1:]:
        line = line.strip()
        if line.startswith("Image Prompt:"):
            if current_scene["image_prompt"]:
                scenes.append(current_scene)
                current_scene = {"image_prompt": "", "motion_prompt": ""}
            mode = "image"
            current_scene["image_prompt"] = line.replace("Image Prompt:", "").strip()
        elif line.startswith("Motion Prompt:"):
            mode = "motion"
            current_scene["motion_prompt"] = line.replace("Motion Prompt:", "").strip()
        elif line:
            if mode == "image":
                current_scene["image_prompt"] += " " + line
            elif mode == "motion":
                current_scene["motion_prompt"] += " " + line

    if current_scene["image_prompt"]:
        scenes.append(current_scene)

    return title, scenes

# === GENERATE VOICE PAYLOAD ===
def generate_voice_payload(text):
    return {
        "voice_id": "j9jfwdrw7BRfcR43Qohk",
        "model_id": "eleven_multilingual_v2",
        "text": text,
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}
    }

# === GENERATE VIDEO WORKFLOW ===
def generate_video_workflow(title, scenes):
    return {
        "workflow": {
            "title": title,
            "type": "dreamloop-video",
            "scenes": scenes
        }
    }

# === WRITE JSON ===
def write_json(data, path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# === WRITE YAML ===
def write_yaml(data, path: str) -> None:
    def _to_yaml(obj, indent=0):
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
        return [f"{space}{obj}"]

    with open(path, "w") as f:
        f.write("\n".join(_to_yaml(data)))

# === GIT PUSH ===
def push_to_github(message="Auto commit"):
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push"], check=True)

# === FULL WORKFLOW ===
def run():
    title, scenes = parse_memory_file(MEMORY_FILE)
    print(f"[✓] Workflow created for: Dreamloop Memory: {title}")
    voice_payload = generate_voice_payload(title)
    workflow = generate_video_workflow(title, scenes)

    write_json(voice_payload, VOICE_PAYLOAD_FILE)
    write_json(scenes, SCENE_PROMPTS_FILE)
    write_yaml(workflow, VIDEO_WORKFLOW_FILE)

    push_to_github("🌀 Auto-generated Dreamloop video workflow")

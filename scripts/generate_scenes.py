import json
import os
import requests
from pathlib import Path

SCENE_PROMPTS_FILE = "scene_prompts.json"
OUTPUT_DIR = "video"
COMFYUI_URL = "http://localhost:8188/prompt"


def run():
    """Generate scene videos using the ComfyUI API."""
    path = Path(SCENE_PROMPTS_FILE)
    if not path.exists():
        raise FileNotFoundError(f"Missing {SCENE_PROMPTS_FILE}")

    scenes = json.loads(path.read_text())
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for idx, scene in enumerate(scenes, 1):
        try:
            resp = requests.post(COMFYUI_URL, json=scene)
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"[error] Failed to generate scene {idx}: {exc}")
            continue

        out_path = f"{OUTPUT_DIR}/scene_{idx:02d}.mp4"
        with open(out_path, "wb") as fh:
            fh.write(resp.content)
        print(f"[+] Scene {idx} saved to {out_path}")

if __name__ == "__main__":
    run()

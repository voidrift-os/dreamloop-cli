import json
from pathlib import Path
from codex_dreamloop_workflow import (
    parse_memory_file,
    generate_voice_payload,
    generate_scene_prompts,
    generate_video_workflow,
    MEMORY_FILE,
)

VOICE_PAYLOAD_FILE = "voice_payload.json"
SCENE_PROMPTS_FILE = "scene_prompts.json"
VIDEO_WORKFLOW_FILE = "video_workflow.json"


def run():
    """Parse the Dreamloop memory file and emit all workflow JSONs."""
    memory_path = Path(MEMORY_FILE)
    if not memory_path.exists():
        raise FileNotFoundError(f"Missing {MEMORY_FILE}")

    title, scenes = parse_memory_file(memory_path)
    full_script = "\n".join([s["prompt"] for s in scenes])

    with open(VOICE_PAYLOAD_FILE, "w") as fh:
        json.dump(generate_voice_payload(full_script), fh, indent=2)

    with open(SCENE_PROMPTS_FILE, "w") as fh:
        json.dump(generate_scene_prompts(scenes), fh, indent=2)

    with open(VIDEO_WORKFLOW_FILE, "w") as fh:
        json.dump(generate_video_workflow(title, scenes), fh, indent=2)

    print(
        f"[+] Generated {VOICE_PAYLOAD_FILE}, {SCENE_PROMPTS_FILE}, {VIDEO_WORKFLOW_FILE}"
    )

if __name__ == "__main__":
    run()

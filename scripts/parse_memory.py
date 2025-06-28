from pathlib import Path

MEMORY_FILE = "dreamloop_memory.md"

def parse_script(path: str = MEMORY_FILE):
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Missing {path_obj}")

    content = path_obj.read_text()
    scenes = []
    for block in content.split("---"):
        if "Scene" in block:
            lines = block.strip().splitlines()
            text = next((l.replace("Prompt:", "").strip() for l in lines if l.startswith("Prompt:")), "")
            scenes.append({"text": text})
    return scenes

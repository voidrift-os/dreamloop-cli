from codex_dreamloop_workflow import (
    parse_memory_file,
    generate_voice_payload,
    write_json,
    write_yaml,
    push_to_github,
    VIDEO_WORKFLOW_FILE,
    VOICE_PAYLOAD_FILE,
    SCENE_PROMPTS_FILE,
)

from scripts import (
    gen_voice_clip,
    generate_scenes,
    assemble_video,
)

def run_full():
    """Run the entire Dreamloop pipeline."""
    try:
        print("[1] Parsing memory and generating JSON/YAML payloads...")
        title, scenes = parse_memory_file("dreamloop_memory.md")

        write_json(scenes, SCENE_PROMPTS_FILE)
        write_json(generate_voice_payload(title), VOICE_PAYLOAD_FILE)
        write_yaml({
            "workflow": {
                "title": title,
                "type": "dreamloop-video",
                "scenes": scenes
            }
        }, VIDEO_WORKFLOW_FILE)

        print("[2] Generating voiceover...")
        gen_voice_clip.run()

        print("[3] Generating scenes...")
        generate_scenes.run()

        print("[4] Assembling final video...")
        assemble_video.run()

        print("[5] Pushing to GitHub...")
        push_to_github("🚀 Dreamloop pipeline executed")

    except Exception as e:
        print("❌ Pipeline failed:", e)

if __name__ == "__main__":
    run_full()

from codex_dreamloop_workflow import (
    parse_memory_file,
    generate_voice_payload,
    generate_scene_prompts,
    generate_video_workflow,
    write_yaml,
    push_to_github,
    VOICE_PAYLOAD_FILE,
    SCENE_PROMPTS_FILE,
    VIDEO_WORKFLOW_FILE,
    ELEVENLABS_VOICE_ID,
)

from scripts import (
    gen_voice_clip,
    generate_scenes,
    assemble_video,
)


def run_full():
    """Run the entire Dreamloop pipeline."""
    try:
        print("[1] Parsing memory and generating payloads...")
        title, scenes = parse_memory_file("dreamloop_memory.md")
        full_script = "\n".join([s["prompt"] for s in scenes])

        voice_payload = generate_voice_payload(f"{title}\n{full_script}", ELEVENLABS_VOICE_ID)
        scene_prompts = generate_scene_prompts(scenes)
        workflow = generate_video_workflow(title, scenes)

        with open(VOICE_PAYLOAD_FILE, "w") as fh:
            json.dump(voice_payload, fh, indent=2)
        with open(SCENE_PROMPTS_FILE, "w") as fh:
            json.dump(scene_prompts, fh, indent=2)
        write_yaml(workflow, VIDEO_WORKFLOW_FILE)

        print("[2] Generating voiceover clip...")
        gen_voice_clip.run()

        print("[3] Generating scene videos via ComfyUI...")
        generate_scenes.run()

        print("[4] Assembling final video with ffmpeg...")
        assemble_video.run()

        print("[5] Pushing results to GitHub...")
        push_to_github("🚀 Dreamloop pipeline executed")

        print("[✓] Dreamloop pipeline complete. Output saved to final_video.mp4")
    except Exception as exc:
        print(f"[error] Pipeline failed: {exc}")
        raise

if __name__ == "__main__":
    run_full()

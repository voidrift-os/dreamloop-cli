from scripts import (
    parse_script_and_generate_jsons,
    gen_voice_clip,
    generate_scenes,
    assemble_video,
    push_to_github,
)


def run_full():
    """Run the entire Dreamloop pipeline."""
    try:
        print("[1] Parsing memory and generating JSON payloads...")
        parse_script_and_generate_jsons.run()

        print("[2] Generating voiceover clip...")
        gen_voice_clip.run()

        print("[3] Generating scene videos via ComfyUI...")
        generate_scenes.run()

        print("[4] Assembling final video with ffmpeg...")
        assemble_video.run()

        print("[5] Pushing results to GitHub...")
        push_to_github.run()

        print("[✓] Dreamloop pipeline complete. Output saved to final_video.mp4")
    except Exception as exc:
        print(f"[error] Pipeline failed: {exc}")
        raise


if __name__ == "__main__":
    run_full()

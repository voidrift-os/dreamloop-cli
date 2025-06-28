from scripts.parse_memory import parse_script
from scripts.voice_server import create_voice_clip
from scripts.gen_image_prompts import generate_image_prompts
from scripts.run_motion import run_motion
from scripts.assemble_video import assemble_video

def main():
    print("[\u2713] Parsing script from memory...")
    scenes = parse_script()

    print("[\u2713] Generating voice with ElevenLabs...")
    for scene in scenes:
        create_voice_clip(scene["text"])

    print("[\u2713] Creating image prompts...")
    generate_image_prompts(scenes)

    print("[\u2713] Generating motion from images...")
    run_motion()

    print("[\u2713] Assembling video...")
    assemble_video()

    print("[\u2714] Dreamloop short complete. Check /output for final video.")

if __name__ == '__main__':
    main()

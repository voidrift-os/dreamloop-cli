import glob
import os
import subprocess

VOICE_CLIP = "voice/dreamloop_voice.mp3"
VIDEO_DIR = "video"
OUTPUT_FILE = "final_video.mp4"


def run():
    """Concatenate scene clips and overlay the generated voiceover."""
    scene_files = sorted(glob.glob(os.path.join(VIDEO_DIR, "scene_*.mp4")))
    if not scene_files:
        raise FileNotFoundError("No scene videos found")
    if not os.path.exists(VOICE_CLIP):
        raise FileNotFoundError(f"Missing voice clip: {VOICE_CLIP}")

    list_file = os.path.join(VIDEO_DIR, "scenes.txt")
    with open(list_file, "w") as fh:
        for path in scene_files:
            fh.write(f"file '{path}'\n")

    combined = os.path.join(VIDEO_DIR, "combined.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", combined
    ], check=True)

    subprocess.run([
        "ffmpeg", "-y", "-i", combined, "-i", VOICE_CLIP, "-c:v", "copy", "-c:a", "aac", "-shortest", OUTPUT_FILE
    ], check=True)

    print(f"[+] Final video created at {OUTPUT_FILE}")

if __name__ == "__main__":
    run()

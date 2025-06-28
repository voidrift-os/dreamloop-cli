import subprocess

FILES = [
    "voice_payload.json",
    "scene_prompts.json",
    "video_workflow.yaml",
    "voice/dreamloop_voice.mp3",
    "video",
    "final_video.mp4",
]


def run(commit_msg="\ud83d\ude80 Auto-generated Dreamloop video workflow"):
    """Commit generated files and push to GitHub."""
    try:
        subprocess.run(["git", "add", *FILES], check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("[+] Pushed results to GitHub")
    except subprocess.CalledProcessError as exc:
        print(f"[error] Git push failed: {exc}")
        raise

if __name__ == "__main__":
    run()

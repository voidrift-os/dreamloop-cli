# Dreamloop CLI

This CLI tool helps you generate AI-driven cinematic shorts based on Dreamloop-style scripts using:
- ElevenLabs API for voice
- Stable Diffusion/DALL·E for images
- AnimateDiff or ffmpeg for motion
- ffmpeg to assemble the final video

## Folder Structure
- `scenes/`: Text scripts per scene
- `images/`: Image prompts or outputs
- `voice/`: Voiceover mp3 files
- `video/`: Assembled video segments
- `scripts/`: Helper scripts

## Basic Workflow
1. Write your 5-scene script in `scenes/`
2. Run `scripts/voice_server.py` to start a local API for voice generation (ElevenLabs)
3. Use image generation tools to create scene PNGs
4. Use `ffmpeg` to combine image + audio per scene
5. Concatenate all scenes into a final short
6. Run `scripts/start_dreamloop.sh` to trigger the full Dreamloop pipeline

## Creating a starter memory file
Generate a placeholder `dreamloop_memory.md` using the `dreamloop-init` command:

```bash
python dreamloop_init.py
```

## Using ComfyUI for Motion
If you want to generate motion via AnimateDiff, install **ComfyUI** and the **AnimateDiff** extension first. Missing these will cause errors like `node types were not found` when loading the workflow.

1. Clone [ComfyUI](https://github.com/comfyanonymous/ComfyUI) and install its dependencies.
2. In ComfyUI's `custom_nodes/` folder, clone or copy the AnimateDiff extension. For example:
   ```bash
   cd path/to/ComfyUI/custom_nodes
   git clone https://github.com/your-animdiff-repo/AnimateDiff.git
   ```
3. Restart ComfyUI so it loads the new nodes.
4. Reload your workflow. The nodes (`Load Checkpoint`, `AnimateDiffLoader`, etc.) should be recognized, and the zod validation errors will disappear.


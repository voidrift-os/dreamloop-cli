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
2. Use `scripts/gen_voice.py` to generate voiceovers (ElevenLabs API)
3. Use image generation tools to create scene PNGs
4. Use `ffmpeg` to combine image + audio per scene
5. Concatenate all scenes into a final short


def generate_image_prompts(scenes):
    for i, scene in enumerate(scenes, 1):
        print(f"[image] Prompt for scene {i}: {scene.get('text', '')}")

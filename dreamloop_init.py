import click
from pathlib import Path

DEFAULT_CONTENT = """# Dreamloop Memory\n\nScene 1\nPrompt: A short description of your first scene\nMotion: Camera pans in\n---\nScene 2\nPrompt: A second scene description\nMotion: Camera pans out\n"""

@click.command("dreamloop-init")
@click.argument("path", default="dreamloop_memory.md")
def dreamloop_init(path):
    """Create a default dreamloop memory file."""
    p = Path(path)
    if p.exists():
        click.echo(f"{path} already exists")
        return
    p.write_text(DEFAULT_CONTENT)
    click.echo(f"Created {path}")

if __name__ == "__main__":
    dreamloop_init()

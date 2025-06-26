import os
import openai

# Set your OpenAI API key or define the OPENAI_API_KEY environment variable
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-REPLACE_WITH_YOUR_KEY")


def run_codex_command(prompt: str) -> None:
    """Send the prompt to the model and execute the returned command."""
    try:
        api_version = getattr(openai, "__version__", "0")
        major_version = int(api_version.split(".")[0]) if api_version[0].isdigit() else 0

        chat_args = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a CLI automation assistant that controls Dreamloop CLI. "
                        "Only return shell commands that operate in the project folder."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }

        if major_version >= 1:
            response = openai.ChatCompletion.create(**chat_args)
        else:
            response = openai.chat.completions.create(**chat_args)

        command = response["choices"][0]["message"]["content"].strip()
        print(f"💡 Codex says: {command}")
        os.system(command)
    except Exception as e:
        print(f"⚠️ Error: {e}")


if __name__ == "__main__":
    print("🧠 Dreamloop Codex Terminal Online (v1.x API)")
    print("Type your command. Type 'exit' to stop.")
    while True:
        user_input = input("🌀 > ")
        if user_input.lower() in ["exit", "quit"]:
            break
        run_codex_command(user_input)

import os
import openai

# Replace this with your actual OpenAI API key
openai.api_key = "sk-REPLACE_WITH_YOUR_KEY"

def run_codex_command(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a CLI automation assistant that controls Dreamloop CLI. Only return shell commands that operate in the project folder."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    command = response.choices[0].message["content"].strip()
    print(f"💡 Codex says: {command}")
    os.system(command)

if __name__ == "__main__":
    print("🧠 Dreamloop Codex Controller Initialized.")
    print("Type natural language instructions. Type 'exit' to quit.")
    while True:
        user_input = input("🧠 Dreamloop > ")
        if user_input.lower() in ["exit", "quit"]:
            break
        run_codex_command(user_input)

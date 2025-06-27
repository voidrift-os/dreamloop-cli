import os
from openai import OpenAI

# ✅ Load API Key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("\U0001F9E0 Dreamloop Codex Terminal Online (v1.x API)")
print("Type your command. Type 'exit' to stop.")

while True:
    prompt = input("\U0001F300 > ")
    if prompt.lower() in ["exit", "quit"]:
        print("Exiting Dreamloop Codex...")
        break

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are Codex, an advanced dreamcore simulation scriptwriter.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        output = response.choices[0].message.content.strip()
        print("\n\u2728 Result:\n")
        print(output)
        print("\n" + ("-" * 40) + "\n")
    except Exception as e:
        print(f"\u26A0\uFE0F Error: {e}\n")

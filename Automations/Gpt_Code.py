from groq import Groq
from dotenv import dotenv_values

env = dotenv_values(".env")
client = Groq(api_key=env.get("GroqApiKey"))

def generate_code(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

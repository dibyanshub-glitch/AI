# RealtimeSearchEngine.py
from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
import os
from dotenv import dotenv_values
import traceback

import requests

# -------------------------
# Config / env
# -------------------------
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
AssistantName = env_vars.get("AssistantName", "Assistant")
GroqApiKey = env_vars.get("GroqApiKey")

if not GroqApiKey:
    print("[ERROR] GroqApiKey not found in .env. Set GroqApiKey=<your_key> and restart.")
client = None
try:
    if GroqApiKey:
        client = Groq(api_key=GroqApiKey)
except Exception as e:
    print("[ERROR] Failed to construct Groq client:", e)
    traceback.print_exc()
    client = None

# Ensure Data folder exists
os.makedirs("Data", exist_ok=True)
CHATLOG_PATH = os.path.join("Data", "ChatLog.json")
if not os.path.exists(CHATLOG_PATH):
    with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
        dump([], f)

# -------------------------
System = (
    f"Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {AssistantName} "
    "which has real-time up-to-date information from the internet.\n"
    
    "*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***\n"
    "*** Just answer the question from the provided data in a professional way. ***"
)

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello! How can I assist you today?"},
    {"role": "user", "content": "What is the current date and time?",
     "name": "get_time"},
    {"role": "assistant", "content": "The current date and time is [current_time]."},
    {"role": "user", "content": "What is the latest news on technology?",
     "name": "get_news"},
    {"role": "assistant", "content": "The latest news on technology is [latest_tech_news]."},
    {"role": "user", "content": "What is the weather like in New York City?", "name": "get_weather"},
    {"role": "assistant", "content": "The weather in New York City is [current_weather_nyc]."}
]

# -------------------------
def GoogleSearch(query):
    try:
        results = list(search(query, advanced=True, num_results=5))
    except TypeError:
        # Some versions of googlesearch may not accept advanced/num_results
        results = list(search(query, num=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"
    for i in results:
        # results items can be objects with title/link/description or plain strings; be defensive
        title = getattr(i, "title", None) or i if isinstance(i, str) else getattr(i, "title", "")
        link = getattr(i, "link", None) or (i if isinstance(i, str) else getattr(i, "link", ""))
        desc = getattr(i, "description", "") or ""
        Answer += f"Title: {title}\nLink: {link}\nDescription: {desc}\n\n"
    Answer += "[end]"
    return Answer

def AnswerModifier(answer: str) -> str:
    lines = answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

def Information() -> str:
    now = datetime.datetime.now()
    return (
        "Use This Real-time Information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"The current time is {now.strftime('%H:%M:%S')}.\n"
        f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}.\n"
        f"Current timestamp: {int(now.timestamp())}\n"
        f"latest news on technology: [latest_tech_news]\n"
        f"weather in New York City: [current_weather_nyc]\n"
        
    )

# -------------------------
def _load_messages():
    try:
        with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
            data = load(f)
            if not isinstance(data, list):
                return []
            return data
    except Exception:
        return []

def _save_messages(msgs):
    try:
        with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
            dump(msgs, f, indent=4, ensure_ascii=False)
    except Exception:
        traceback.print_exc()

# -------------------------
def RealtimeSearchEngine(prompt: str) -> str:
    try:
        news_data = ""

        # =========================
        # 📰 1. TRY NEWS API FIRST
        # =========================
        if NewsApiKey := env_vars.get("NewsApiKey"):
            try:
                url = f"https://newsapi.org/v2/everything?q={prompt}&sortBy=publishedAt&language=en&apiKey={NewsApiKey}"
                response = requests.get(url).json()

                articles = response.get("articles", [])[:5]

                if articles:
                    news_data = "Latest News:\n"
                    for i, article in enumerate(articles, 1):
                        title = article["title"]
                        source = article["source"]["name"]
                        news_data += f"{i}. {title} ({source})\n\n"
            except Exception as e:
                print("News API error:", e)

        # =========================
        # 🌐 2. GOOGLE FALLBACK
        # =========================
        if not news_data:
            try:
                search_data = GoogleSearch(prompt)
                news_data = search_data[:1500]
            except Exception as e:
                print("Google search error:", e)
                news_data = "No real-time data found."

        # =========================
        # 🤖 3. AI EXPLANATION (GROQ)
        # =========================
        if client:
            try:
                payload_messages = [
                    {
                        "role": "system",
                        "content": "You are a real-time AI assistant. Provide detailed, clear, and professional answers using given data."
                    },
                    {
                        "role": "system",
                        "content": Information()
                    },
                    {
                        "role": "system",
                        "content": news_data
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]

                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=payload_messages,
                    temperature=0.5,
                    max_tokens=500
                )

                answer = completion.choices[0].message.content.strip()
                return AnswerModifier(answer)

            except Exception as e:
                print("Groq error:", e)

        # =========================
        # 📤 4. FALLBACK OUTPUT
        # =========================
        return news_data

    except Exception as e:
        print("[ERROR] RealtimeSearchEngine failed:", e)
        traceback.print_exc()
        return "Failed to fetch real-time information."
    
if __name__ == "__main__":
    try:
        while True:
            prompt_text = input("Enter your query: ").strip()
            if not prompt_text:
                continue
            print(RealtimeSearchEngine(prompt_text))
    except KeyboardInterrupt:
        print("\nExiting.")

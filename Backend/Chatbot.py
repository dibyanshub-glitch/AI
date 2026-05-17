
from groq import Groq
import json
import datetime
from dotenv import dotenv_values
import os
import traceback


# Ensure Data folder exists
os.makedirs("Data", exist_ok=True)

env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
AssistantName = env_vars.get("AssistantName", "Assistant")
GroqApiKey = env_vars.get("GroqApiKey")

if not GroqApiKey:
    print("[ERROR] GroqApiKey not found in .env. Set GroqApiKey=<your_key>")

# Build client
client = None
try:
    if GroqApiKey:
        client = Groq(api_key=GroqApiKey)
except Exception as e:
    print("[ERROR] Failed to construct Groq client:", e)
    traceback.print_exc()

CHATLOG_PATH = os.path.join("Data", "ChatLog.json")

# Ensure chatlog exists
if not os.path.exists(CHATLOG_PATH):
    with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, indent=4)

System = f"""
You are {AssistantName}, an elite AI developer and professional content writer.
You are {AssistantName}, a highly professional AI assistant.

STYLE:
- Speak naturally and conversationally
- Be concise but helpful
- Sound like ChatGPT or Alexa
- No robotic repetition
- No unnecessary self-introduction

PERSONALITY:
- Calm
- Smart
- Helpful
- Human-like

Always respond naturally to the user's intent

GOALS:
- Maintain conversation context
- Remember what the user said earlier
- Speak naturally like ChatGPT voice mode
- Be warm, calm, and human-like
- Avoid robotic repetition

Rules:
- NEVER say "I am a text-based AI"
- NEVER mention knowledge cutoff
- Always act like real-time intelligent assistant
- If unsure → say "Fetching latest data"

CONVERSATION RULES:
- If user continues same topic → continue smoothly
- If user changes topic → adapt naturally
- Ask short follow-up questions when appropriate
- Do NOT overtalk
- Keep responses conversational

PERSONALITY:
- Smart
- Friendly
- Professional
- Slightly casual

IMPORTANT:
You must remember previous conversation from chat history and respond contextually

You must NOT include extra text when triggering automation.
"""


SystemChatBot = [
    {"role": "system", "content": System}
]

# Real-time information function to provide current date, time, and other dynamic info to the assistant

def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Today is {now.strftime('%A')}, {now.strftime('%d %B %Y')}.\n"
        f"Current time: {now.strftime('%H:%M:%S')}.\n"
        f"\nRemember, you are {AssistantName}, an AI chatbot created by {Username}.\n"
        f"Hey {Username}, how can I assist you today?"
        f"The latest news is{' [Insert latest news here]' if False else ' [News data not available]'}.\n"
        f"You have access to your memory and can recall or forget information as needed. Always be helpful and concise in your responses."
        f"\nIf you need to remember something, use the format: remember (key) is (value). For example, 'remember my favorite color is blue'."
        f"\nTo recall something, use: recall (key). For example, 'recall my favorite color'. To forget something, use: forget (key). For example, 'forget my favorite color'."  
        f"\nYou can also perform tasks like opening applications, searching the web, or writing content. Always respond in a helpful and concise manner."   
        f"\nCurrent date and time is provided to help you give accurate responses. Always be friendly and concise in your answers."
        f"\nIf user requests writing, coding, or generating scripts, always respond strictly using:content <topic>. Never include explanation."
        f"\nIf you are asked to perform a google search for a specific topic, respond with 'google search (topic)'. For example, if asked to search for the latest news on technology, respond with 'google search latest news on technology'."
        f"\nIf you are asked to perform a youtube search for a specific topic, respond with 'youtube search (topic)'. For example, if asked to search for cooking tutorials, respond with 'youtube search cooking tutorials'."  
        f"\nAlways remember to keep your responses concise, helpful, and friendly. You are a powerful AI assistant designed to assist with a wide range of tasks while maintaining a friendly and approachable demeanor."   
        f"\nIf user asks about latest or today's information, you must answer using real-time knowledge when available and never mention knowledge cutoff."
    )

# Answer modifier to clean up the assistant's response by removing extra whitespace and ensuring proper formatting
def AnswerModifier(answer: str) -> str:
    lines = [ln.rstrip() for ln in answer.splitlines() if ln.strip()]
    return "\n".join(lines)

# Main chatbot function that takes user input, processes it, and generates a response using the Groq API while maintaining conversation context and applying necessary formatting and rules
def ChatBot(Query: str) -> str:
    """
    Safe Groq chatbot with token protection
    """
    global client

    if client is None:
        return "[ERROR] Groq client not initialized."

    try:
        # 🔒 HARD LIMIT USER INPUT
        Query = Query[:1200]
        # 🔥 Auto upgrade writing prompts
        lower_q = Query.lower()

# =========================
# 💻 CODE MODE
# =========================
        if "code" in lower_q or "program" in lower_q or "script" in lower_q:

            Query = f"""
        Generate clean and correct code.

        Task: {Query}

        Rules:
        - Only code output
        - No explanation
        - No markdown
        - Proper indentation
        - Ready to run
        """

        # =========================
        # 📝 TEXT MODE (APPLICATION)
        # =========================
        elif any(word in lower_q for word in ["application", "letter", "email", "leave", "request"]):

            Query = f"""
        Write a professional and clean application.

        Topic: {Query}

        Rules:
        - No spelling mistakes
        - No code or symbols
        - Proper format:
        To,
        Subject,
        Respected Sir/Madam,
        Body,
        Thank you,
        Yours sincerely

        Only return the final application.
        """


        # Load chat history
        try:
            with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
                messages = json.load(f)
                if not isinstance(messages, list):
                    messages = []
        except Exception:
            messages = []
            
        if not all(isinstance(m, dict) and "role" in m and "content" in m for m in messages):
            messages = []


        # Append user message
        messages.append({"role": "user", "content": Query})
# ⭐ persist user message
        try:
            with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
                full_log = json.load(f)
                if not isinstance(full_log, list):
                    full_log = []
        except Exception:
            full_log = []

        full_log.append({"role": "user", "content": Query})

        with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
            json.dump(full_log, f, indent=4, ensure_ascii=False)
        # 🧹 sanitize messages
        clean_messages = []

        for msg in messages:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                clean_messages.append({
                    "role": str(msg["role"]),
                    "content": str(msg["content"])
                })

        MAX_HISTORY_MESSAGES = 20
        messages = clean_messages[-MAX_HISTORY_MESSAGES:]

        send_messages = (
            SystemChatBot
            + [{"role": "system", "content": RealtimeInformation()}]
            + messages
        )

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=send_messages,
            max_tokens=1200,   # 🔒 OUTPUT LIMIT
            temperature=0.7,
            top_p=1,
            # stream=True,
        )


        Answer = completion.choices[0].message.content


        Answer = Answer.replace("</s>", "")
        Answer = Answer.replace("```", "")
        Answer = AnswerModifier(Answer)

        # Save back to chat log
       # ---------- SAFE CHAT LOG SAVE ----------
        try:
            with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
                full_log = json.load(f)
                if not isinstance(full_log, list):
                    full_log = []
        except Exception:
            full_log = []

        full_log.append({"role": "assistant", "content": Answer})

        with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
            json.dump(full_log, f, indent=4, ensure_ascii=False)
        
        # Detect programming language hints
        if "python" in Query.lower():
            Answer = "# Python Code\n\n" + Answer

        elif "html" in Query.lower():
            Answer = "<!-- HTML Code -->\n\n" + Answer


        return Answer

    except Exception as e:
        print("[ERROR] ChatBot exception:", e)
        traceback.print_exc()
        return "⚠️ I am busy right now, please try again."

# Simple command-line interface for testing the chatbot
if __name__ == "__main__":
    try:
        while True:
            user_input = input("Enter Your Question: ").strip()
            if not user_input:
                continue
            reply = ChatBot(user_input)
            print("\n" + reply + "\n")
    except KeyboardInterrupt:
        print("\nExiting.")
        os.exit(0)

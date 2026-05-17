
from Automations.DeveloperMode import memory
from Backend.SpeechToText_Whisper import SpeechRecognitionStream as SpeechRecognition
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.Automation import GenerateAndSaveCode
# from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TExtToSpeech
from Automations.Greeting import startup_greeting
# from Automations.SmartCodeWriter import smart_code_writer
from Backend.ImageGeneration import engine
# from PyQt5.QtWidgets import QApplication
from Backend.MemoryBrain import remember, recall, forget
# from Automations.DeveloperMode.brain import developer_mode
from Automations.AutonomousBrain.scheduler import autonomous_loop
from Backend.core import set_main_executor
from Backend.Voice_Automation import run_voice_automations_async
from dotenv import dotenv_values
from Backend.state import AUTONOMOUS_MODE, MAIN_LOOP
import Backend.state as state
from Backend.core import set_main_executor
from time import sleep
import json
import getpass
import eel
import os
import threading
import time
import socket
import asyncio

# 🎯 GLOBAL VOICE STATE
SHUTTING_DOWN = False
INTERRUPT_ENABLED = False
INTERRUPT_THRESHOLD = 0.65  # voice energy threshold
# =============================
INTERRUPT_ENERGY = 0.04
LAST_USER_TEXT = ""
LAST_USER_TIME = 0
WAKE_ACTIVE = False
WAKE_TIMEOUT = 8  # seconds
LAST_WAKE_TIME = 0
IS_LISTENING = False
IS_SPEAKING = False
STOP_SPEAKING = False
MIC_ACTIVE = False
LAST_SPEAK_TIME = 0
VOICE_COOLDOWN = 3.0  # seconds to ignore mic after speaking

# ============================
# GLOBAL CHATBOT STATE
# ===========================
import warnings
warnings.filterwarnings("ignore")

SESSION_FILE = "Data/session.json"
def save_session(email):
    with open(SESSION_FILE, "w") as f:
        json.dump({"user": email}, f)


def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE, "r") as f:
        data = json.load(f)
        return data.get("user")


def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        
# ================= SUBSCRIPTION =================

SUBSCRIPTION_FILE = "Data/subscription.json"

def load_subscription():
    if not os.path.exists(SUBSCRIPTION_FILE):
        return {"plan": "free", "expires": None}
    with open(SUBSCRIPTION_FILE, "r") as f:
        return json.load(f)

def save_subscription(data):
    with open(SUBSCRIPTION_FILE, "w") as f:
        json.dump(data, f, indent=2)

@eel.expose
def getSubscription():
    return load_subscription()

@eel.expose
def upgradePlan(plan):
    data = {
        "plan": plan,
        "expires": "2026-12-31"
    }
    save_subscription(data)
    return {"success": True}


# ================= CHAT CONTROL =================

@eel.expose
def newChat():
    from Backend.conversation_memory import memory
    memory.clear()

    with open("Data/ChatLog.json", "w") as f:
        json.dump([], f)

    return {"success": True}


@eel.expose
def exportChat():
    path = "Data/ChatLog.json"
    if not os.path.exists(path):
        return ""
    with open(path, "r") as f:
        return f.read()


# ================= CONTACT STORAGE =================

@eel.expose
def saveContact(name, email, message):
    os.makedirs("Data", exist_ok=True)
    path = "Data/contact_messages.json"

    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append({
        "name": name,
        "email": email,
        "message": message,
        "time": time.ctime()
    })

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return {"success": True}
# -----------------------------
# ENV + Safe defaults
# -----------------------------

web_folder = os.path.join(os.path.dirname(__file__), "www")
index_path = os.path.join(web_folder, "index.html")

if not os.path.exists(index_path):
    raise FileNotFoundError(f"Missing file: {index_path}")

eel.init(web_folder)

# ============================================================
# 🛑 CLEAN PROFESSIONAL SHUTDOWN
# ============================================================

def shutdown_lukas():
    global SHUTTING_DOWN

    print("🛑 Lukas shutting down...")

    SHUTTING_DOWN = True

    try:
        import Backend.state as state

        loop = state.MAIN_LOOP

        if loop and loop.is_running():

            async def stop_all():
                tasks = [
                    t for t in asyncio.all_tasks(loop)
                    if t is not asyncio.current_task(loop)
                ]

                for task in tasks:
                    task.cancel()

                await asyncio.gather(*tasks, return_exceptions=True)

            # Run stop coroutine safely
            asyncio.run_coroutine_threadsafe(stop_all(), loop).result(timeout=3)

            loop.call_soon_threadsafe(loop.stop)

    except Exception as e:
        print("Shutdown loop error:", e)

    try:
        eel.closeWindow()
    except:
        pass

    time.sleep(0.5)

    os._exit(0)
# =============================
# TEMP SAFE FUNCTIONS
# =============================
async def speak_async(text):
    global IS_SPEAKING, LAST_SPEAK_TIME

    print("🔊 SPEAK:", text)

    IS_SPEAKING = True

    # Just enqueue speech
    TExtToSpeech(text)

    # small non-blocking delay
    await asyncio.sleep(0.1)

    IS_SPEAKING = False
    LAST_SPEAK_TIME = time.time()
    
# ============================
# ENV + Safe defaults
# ============================

env_vars = dotenv_values(".env") or {}

Username = (
    env_vars.get("Username")
    or env_vars.get("USERNAME")
    or os.getenv("USERNAME")
    or getpass.getuser()
    or "User"
)

AssistantName = (
    env_vars.get("AssistantName")
    or env_vars.get("Assistantname")
    or env_vars.get("ASSISTANT_NAME")
    or "Jarvis"
)

DefaultMessage = f'''{Username} : Hello {AssistantName}, How are you?
{AssistantName} : Welcome {Username}, I am doing great! How can I assist you today?'''

subprocesses = []

# =============================
# AVAILABLE COMMANDS
# =============================

functions = [
    "open", "close", "play", "system", "content",
    "google search", "youtube search", "wikipedia", "search", "find"
]

os.makedirs("Data", exist_ok=True)
os.makedirs(os.path.join("Frontend", "Files"), exist_ok=True)

# -----------------------------
# Helpers for chat logs / GUI
# -----------------------------
def find_free_port(start=8000, max_tries=50):
    for port in range(start, start + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return port
            except OSError:
                continue
    raise OSError("No available port found.")

def format_code(code: str):
    lines = code.split("\n")
    clean = []

    for line in lines:
        clean.append(line.rstrip())

    return "\n".join(clean).strip()

def start():
    playAssistantSound()  # ← MOVE HERE

    port = find_free_port(8000)
    # url = f"http://localhost:{port}/index.html"
    print(f"🟢 Starting Eel on {port}")

   
    eel.start(
    "index.html",
    mode="chrome",
    host="localhost",
    port=port,
    block=True,
    cmdline_args=["--auto-open-devtools-for-tabs"]
)


# =============================
# INITIALIZE EEL EXPOSED FUNCTIONS
# =============================
@eel.expose
def init():
    try:
        eel.hideStart()
        eel.ShowHood()
        eel.DisplayMessage("Lukas ready")
    except Exception as e:
        print("Init error:", e)
        
#============================
# EEL EXPOSED FUNCTIONS (FROM UI)
#============================
@eel.expose
def allCommands(message=""):
    global IS_AUTHENTICATED

    if not IS_AUTHENTICATED:
        return {"error": "NOT_AUTHENTICATED"}

    import asyncio
    try:
        asyncio.run(MainExecution(message))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.create_task(MainExecution(message))

# ============================
# 🎤 VOICE CONTROLLED MAIN LOO
# ============================
@eel.expose
def startListening():
    if not IS_AUTHENTICATED:
        return {"error": "NOT_AUTHENTICATED"}   
    
    """Mic button pressed"""

    global MIC_ACTIVE
    MIC_ACTIVE = True

    print("🎤")

    query = SpeechRecognition()

    if query and query.strip():
        import asyncio
        asyncio.run(MainExecution(query))

    MIC_ACTIVE = False

@eel.expose
def closeApp():
    shutdown_lukas()

@eel.expose
def toggleMic():
    global MIC_ACTIVE
    MIC_ACTIVE = not MIC_ACTIVE
    print("🎤 Mic state:", MIC_ACTIVE)

from Backend.Auth import login_user, register_user
import eel


IS_AUTHENTICATED = False
CURRENT_USER = None

@eel.expose
def lukasLogin(email, password):
    global IS_AUTHENTICATED, CURRENT_USER

    result = login_user(email, password)

    if result.get("ok"):
        IS_AUTHENTICATED = True
        CURRENT_USER = email
        save_session(email)

        start_ai_systems()   # 🔥 START HERE
        startup_greeting()

        return {"success": True}
    else:
        return {"success": False, "message": result.get("msg")}
    
@eel.expose
def lukasRegister(email, password):
    return register_user(email, password)

@eel.expose
def lukasLogout():
    global IS_AUTHENTICATED, CURRENT_USER
    IS_AUTHENTICATED = False
    CURRENT_USER = None
    clear_session()
    return {"success": True}

@eel.expose
def guestLogin():
    global IS_AUTHENTICATED, CURRENT_USER

    IS_AUTHENTICATED = True
    CURRENT_USER = "Guest"

    start_ai_systems()   # 🔥 START HERE
    startup_greeting()

    return {"success": True}

@eel.expose
def setVoice(type):
    print("Voice set to:", type)
    state.VOICE_TYPE = type
    return True


@eel.expose
def toggleAutoListen():
    state.AUTO_LISTEN = not getattr(state, "AUTO_LISTEN", False)
    return state.AUTO_LISTEN


@eel.expose
def toggleBargeIn():
    state.BARGE_ENABLED = not getattr(state, "BARGE_ENABLED", False)
    return state.BARGE_ENABLED


@eel.expose
def toggleWakeWord():
    state.WAKE_WORD = not getattr(state, "WAKE_WORD", False)
    return state.WAKE_WORD


@eel.expose
def toggleBreathing():
    state.BREATHING = not getattr(state, "BREATHING", True)
    return state.BREATHING


@eel.expose
def toggleEmotion():
    state.EMOTION_ENGINE = not getattr(state, "EMOTION_ENGINE", True)
    return state.EMOTION_ENGINE


@eel.expose
def toggleNoise():
    state.NOISE_FILTER = not getattr(state, "NOISE_FILTER", False)
    return state.NOISE_FILTER


@eel.expose
def setIntensity(val):
    state.ORB_INTENSITY = float(val)
    return True

# ============================================
# 🔗 EEL UI HELPERS (CRITICAL)
# ============================================

def ShowTextToScreen(text: str):
    try:
        eel.receiverText(text)
    except:
        pass

def ShowUserText(text: str):
    try:
        eel.senderText(text)
    except:
        pass

def SetAssistantStatus(text: str):
    try:
        eel.DisplayMessage(text)
    except:
        pass
def playAssistantSound():
    """Startup sound placeholder"""
    pass
# ============================================
# 🛠️ TEMP COMPATIBILITY HELPERS
# ============================================

def TempDirectoryPath(filename: str) -> str:
    """Return path inside Data folder"""
    return os.path.join("Data", filename)

def AnswerModifier(text: str) -> str:
    """Pass-through formatter"""
    return text

def QueryModifier(text: str) -> str:
    """Clean query text"""
    return text.strip()


def ShowDefaultChatIfNoChats():
    path = r"Data\ChatLog.json"
    # Create file if it doesn't exist or is too small
    try:
        if not os.path.exists(path) or os.path.getsize(path) < 5:
            # write empty list as default JSON
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

            with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
                file.write("")

            with open(TempDirectoryPath("Response.data"), "w", encoding="utf-8") as file:
                file.write(DefaultMessage)
    except Exception as e:
        print("ShowDefaultChatIfNoChats error:", e)


def ReadChatLogJson():
    path = r"Data\ChatLog.json"
    try:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        print("ReadChatLogJson error:", e)
        return []


def ChatLogIntegration():
    json_data = ReadChatLogJson()
    fromatted_chatlog = ""
    for entry in json_data:
        role = entry.get("role", "").lower()
        content = entry.get("content", "")
        if role == "user":
            fromatted_chatlog += f"User: {content}\n"
        elif role == "assistant":
            fromatted_chatlog += f"Assistant: {content}\n"

    # safe names
    username_safe = str(Username) if Username is not None else "User"
    assistant_safe = str(AssistantName) if AssistantName is not None else "Jarvis"

    formatted_chatlog = fromatted_chatlog.replace("User", username_safe + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", assistant_safe + " ")

    try:
        with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
            file.write(AnswerModifier(formatted_chatlog))
    except Exception as e:
        print("ChatLogIntegration write error:", e)


def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath("Database.data"), "r", encoding="utf-8") as f:
            Data = f.read()
        if Data:
            lines = Data.split("\n")
            result = "\n".join(lines)
            with open(TempDirectoryPath("Response.data"), "w", encoding="utf-8") as f2:
                f2.write(result)
    except Exception as e:
        print("ShowChatsOnGUI error:", e)


def InitialExecution():
    pass

InitialExecution()

# 🚀 FAST-PATH FOR AUTOMATION
def is_automation_command(text: str) -> bool:
    AUTOMATION_PREFIXES = (
        "open ",
        "close ",
        "play ",
        "system ",
        "volume ",
        "mute",
        "unmute",
        "shutdown",
        "restart",
        "send ",
        "whatsapp ",
        "google ",
        "youtube ",
        "notepad",
        "calculator",
    )
    return text.startswith(AUTOMATION_PREFIXES)

# -----------------------------
# MAIN AI LOOP
# -----------------------------

async def MainExecution(Query):

    global LAST_USER_TEXT, LAST_USER_TIME

    if not Query or not Query.strip():
        return False

    # -----------------------------------------
    # 🧾 Display User Message
    # -----------------------------------------
    ShowUserText(Query)

    from Backend.conversation_memory import memory
    memory.add_user(Query)

    # -----------------------------------------
    # 🧹 Normalize Query
    # -----------------------------------------
    quick = Query.lower().strip()

    import string
    punct = string.punctuation.replace(":", "")
    quick = quick.translate(str.maketrans("", "", punct))
    quick = " ".join(quick.split())
    
    # -----------------------------------------
    # 🚫 Duplicate Suppression
    # -----------------------------------------
    
    now = time.time()
    if quick == LAST_USER_TEXT and now - LAST_USER_TIME < 2:
        print("🚫 Duplicate speech ignored")
        return False

    LAST_USER_TEXT = quick
    LAST_USER_TIME = now
    
# ============================================================
# 🖼 IMAGE GENERATION (HIGH PRIORITY)
# ============================================================

    if "generate image" in quick or "generate an image" in quick:

        try:
            prompt = quick.replace("generate image", "")
            prompt = prompt.replace("generate an image", "")
            prompt = prompt.replace("of", "").strip()

            if not prompt:
                prompt = "futuristic ai interface"

            ShowTextToScreen(f"{AssistantName} : Generating image...")
            await speak_async("Generating image")

            await engine.add(prompt)
            await engine.start()

        except Exception as e:
            print("Image engine error:", e)
            ShowTextToScreen(f"{AssistantName} : Image generation failed")
            await speak_async("Image generation failed")

        return True
    
# ============================================================
# 📝 SMART NOTEPAD WRITER (TEXT + CODE SEPARATION)
# ============================================================

    if "notepad" in quick and ("write" in quick or "create" in quick):

        try:
          
         # 1️⃣ Clean and detect intent
            # 🔹 Step 2: Clean prompt
            prompt = quick
            for word in ["open notepad", "write", "create", "generate", "in notepad", "notepad"]:
                prompt = prompt.replace(word, "")

            prompt = prompt.strip()

            # 🔹 Step 3: Detect TYPE
            is_code = any(word in prompt for word in ["code", "website", "app", "program", "script", "project"])

            is_text = any(word in prompt for word in [
                                 "leave", "application", "letter", "request", "sick", "formal", "email", "cover", "resignation", "complaint", "invitation", "proposal"])
            
            if any(word in prompt for word in ["leave", "application", "letter", "request", "email"]):
                is_code = False
                is_text = True
                
            # =========================
            # ✍️ TEXT MODE (APPLICATION)
            # =========================
            if is_text and not is_code:

                ai_prompt = f"""
                     You are a professional English writer.

                     Write a clean and formal application.

                     Topic: {prompt}

                     STRICT RULES:
                     - Only natural English
                     - No code, no symbols, no markdown
                     - No spelling mistakes
                     - Proper format:
                         To,
                         Subject,
                         Respected Sir/Madam,
                         Body,
                         Thank you,
                         Yours sincerely
                     - Keep it simple and professional

                     Application:
                     """

                content = await asyncio.to_thread(ChatBot, ai_prompt)

                # 🔥 CLEAN OUTPUT (VERY IMPORTANT)
                content = content.replace("```", "")
                content = content.replace("*", "")
                content = content.strip()

                # 🔥 REMOVE CODE-LIKE TEXT
                if "def " in content or "{" in content or "}" in content:
                    content = content.replace("{", "").replace("}", "")

                # 🔥 FIX GRAMMAR (AUTO SPELL FIX)
                try:
                    import language_tool_python
                    tool = language_tool_python.LanguageTool('en-US')
                    matches = tool.check(content)
                    content = language_tool_python.utils.correct(content, matches)
                except:
                    pass

                ShowTextToScreen(f"{AssistantName} : Writing application in Notepad")
                await speak_async("Writing application")
                
            # =========================
            # 💻 CODE MODE
            # =========================
            
            else:
                result = GenerateAndSaveCode(prompt)
                content = result["code"]
                
                
                # remove markdown or junk
                content = content.replace("```", "")
                content = content.replace("python", "")
                content = content.replace("html", "")
                content = content.strip()
                
                content = format_code(content)

                # 🔥 DETECT LANGUAGE
                if "def " in content or "import " in content:
                    language = "python"
                elif "<html" in content:
                    language = "html"
                elif "function" in content:
                    language = "javascript"
                elif "css" in content:
                    language = "css"
                else:
                    language = "txt"

                ShowTextToScreen(f"{AssistantName} : Writing code in Notepad")
                await speak_async("Writing code")

            # 🔹 Step 4: Write to Notepad
            from Automations.Editor_writer import write_code_to_editor

            # ✅ FIX: choose language based on mode
            if is_text:
                write_code_to_editor(content, "txt")
            else:
                write_code_to_editor(content, language)

        except Exception as e:
            print("Notepad writer error:", e)
            ShowTextToScreen(f"{AssistantName} : Failed to write ({str(e)})")

        return True
    
# ============================================================
# 🚪 EXIT COMMAND
# ============================================================

    if quick in ("exit", "quit", "close yourself", "shutdown lukas"):
        ShowTextToScreen(f"{AssistantName} : Goodbye!")
        await speak_async("Goodbye. Shutting down Lukas.")
        await asyncio.sleep(1)
        shutdown_lukas()
        return True
    
    # ============================================================
    # 🔥 1️⃣ ABSOLUTE PRIORITY — AUTOMATION ROUTER
    # ============================================================

    AUTOMATION_PREFIXES = (
        "open ",
        "close ",
        "play ",
        "send ",
        "whatsapp ",
        "set alarm",
        "alarm ",
        "calculate ",
        "press ",
        "volume ",
        "mute",
        "unmute",
        "shutdown",
        "restart",

        # 🔥 CAMERA FIX
        "click photo",
        "click my photo",
        "take photo",
        "take my photo",
        "open camera",
        "camera",

        # 🔥 SCREENSHOT FIX
        "take screenshot",
        "take a screenshot",
        "screenshot",

        # others
        "start recording",
        "stop recording",
        "google ",
        "youtube ",
        "search ",
        "find ",
        "notepad",
        "calculator",
        "generate image",
        "remind me",
        "set reminder",
    )

    if any(quick.startswith(prefix) for prefix in AUTOMATION_PREFIXES):

        print("⚙️ PRIORITY: Routing to automation engine")

        if " and " in quick:
            commands = [c.strip() for c in quick.split(" and ")]
        else:
            commands = [quick]

        try:
            results = await Automation(commands)

            if results:
                for r in results:
                    if isinstance(r, str):
                        ShowTextToScreen(f"{AssistantName} : {r}")
                        await speak_async(r)
                    else:
                        ShowTextToScreen(f"{AssistantName} : Done")
                        await speak_async("Done")
            else:
                ShowTextToScreen(f"{AssistantName} : Done")
                await speak_async("Done")

        except Exception as e:
            print("Automation error:", e)
            ShowTextToScreen(f"{AssistantName} : Command failed")
            await speak_async("Command failed")

        return True

    # ============================================================
    # 🧠 2️⃣ MEMORY COMMANDS
    # ============================================================

    if quick.startswith("remember"):
        text = quick.replace("remember", "").strip()
        if " is " in text:
            key, value = text.split(" is ", 1)
            msg = remember(key.strip(), value.strip())
            ShowTextToScreen(f"{AssistantName} : {msg}")
            await speak_async(msg)
            return True

    if quick.startswith("forget"):
        key = quick.replace("forget", "").strip()
        msg = forget(key)
        ShowTextToScreen(f"{AssistantName} : {msg}")
        await speak_async(msg)
        return True

    if quick.startswith("what is") or quick.startswith("who is"):
        key = quick.replace("what is", "").replace("who is", "").strip()
        value = recall(key)
        if value:
            msg = f"{key} is {value}"
            ShowTextToScreen(f"{AssistantName} : {msg}")
            await speak_async(msg)
            return True

    # ============================================================
    # 🌐 3️⃣ REALTIME SEARCH
    # ============================================================

    REALTIME_KEYWORDS = [
    "today news",
    "latest news",
    "current news",
    "what is happening",
    "what's happening",
    "world news",
    "breaking news",
    "today updates",
    "global news",
    "news today",
    "price",
    "current", "now", "rate", "weather",
    "stock", "market", "lpg", "petrol"
    ]

    if any(w in quick for w in REALTIME_KEYWORDS):
        
        print("🌍 REALTIME MODE ACTIVATED")

        SetAssistantStatus("Fetching latest news...")

        Answer = await asyncio.to_thread(RealtimeSearchEngine, Query)

        ShowTextToScreen(f"{AssistantName} : {Answer}")
        await speak_async("Here are the latest updates")
        await speak_async(Answer)
        print("REALTIME QUERY:", Query)
        return True

    # ============================================================
    # 💬 4️⃣ DEFAULT → CHAT MODE
    # ============================================================

    SetAssistantStatus("Thinking...")

    try:
        Answer = await asyncio.to_thread(ChatBot, Query)

        memory.add_assistant(Answer)

        ShowTextToScreen(f"{AssistantName} : {Answer}")
        await speak_async(Answer)

    except Exception as e:
        print("ChatBot error:", e)
        ShowTextToScreen(f"{AssistantName} : I am currently unavailable.")
        await speak_async("I am currently unavailable.")

    return True


# =============================
# 🎧 CONTINUOUS VOICE LOOP
# =============================

async def continuous_voice_loop():
    global IS_LISTENING, IS_SPEAKING, STOP_SPEAKING
    global LAST_SPEAK_TIME, LAST_USER_TEXT, LAST_USER_TIME
    
    if SHUTTING_DOWN:
        return
    print("🎧 Continuous listening started")

    BAD_WORDS = {
        "you", "the", "a", "uh", "um", "",
        "hmm", "huh", "h", "ah", "oh"
    }
    try:
        while not SHUTTING_DOWN:
            if not IS_AUTHENTICATED:
                await asyncio.sleep(0.5)
                continue
            try:
                now = time.time()

                # 🛑 respect manual mic mode
                if MIC_ACTIVE:
                    await asyncio.sleep(0.15)
                    continue

                # =================================================
                # 🛑 Anti-echo cooldown after TTS
                # =================================================
                if now - LAST_SPEAK_TIME < VOICE_COOLDOWN:
                    await asyncio.sleep(0.1)
                    continue

                # =================================================
                # 🎤 MAIN LISTEN
                # =================================================
                if IS_SPEAKING:
                    await asyncio.sleep(0.1)
                    continue

                query = await asyncio.to_thread(SpeechRecognition)
                clean_q = (query or "").strip().lower()

                # 🚫 ignore garbage
                if clean_q in BAD_WORDS or len(clean_q.split()) < 2:
                    await asyncio.sleep(0.08)
                    continue

                # =================================================
                # 🚫 EARLY DUPLICATE SUPPRESSION (CRITICAL)
                # =================================================
                now = time.time()

                if clean_q == LAST_USER_TEXT and now - LAST_USER_TIME < 1.2:
                    print("🚫 Duplicate speech ignored")
                    await asyncio.sleep(0.05)
                    continue

                LAST_USER_TEXT = clean_q
                LAST_USER_TIME = now

                # =================================================
                # ✅ VALID SPEECH
                # =================================================
                print("🗣️ Heard:", query)

                await MainExecution(query)

                await asyncio.sleep(0.05)

            except Exception as e:
                print("Voice loop error:", e)
                await asyncio.sleep(0.4)
    except asyncio.CancelledError:
        print("Voice loop cancelled")
        return
    
# -----------------------------
# THREADS
# -----------------------------

def start_ai_systems():
    if not state.MAIN_LOOP:
        return

    def start_tasks():
        state.MAIN_LOOP.create_task(run_voice_automations_async())
        state.MAIN_LOOP.create_task(autonomous_loop())
        state.MAIN_LOOP.create_task(continuous_voice_loop())
        print("🚀 AI Systems Started")

    state.MAIN_LOOP.call_soon_threadsafe(start_tasks)
    
# =============================
# MAIN ENTRY POINT
# =============================

if __name__ == "__main__":

    import threading
    import asyncio

    state.MAIN_LOOP = asyncio.new_event_loop()
    asyncio.set_event_loop(state.MAIN_LOOP)

    # startup_greeting()

    set_main_executor(MainExecution, state.MAIN_LOOP)

    saved_user = load_session()
    if saved_user:
        IS_AUTHENTICATED = True
        CURRENT_USER = saved_user
    # Start loop in background
    threading.Thread(
        target=state.MAIN_LOOP.run_forever,
        daemon=True
    ).start()

   # 🚀 Start Eel UI
    start()

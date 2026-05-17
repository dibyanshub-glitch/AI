
from AppOpener import close, open as appopen
from webbrowser import open as webopen
# from flask import app
from Backend.AppRegistryScanner import launch_app
# from datetime import datetime
import cv2
import re
# import math
import ast
import operator
import pygetwindow as gw
from pywinauto import Application
import time
# import winsound
import threading
import smtplib
from email.message import EmailMessage
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
# import keyboard
import asyncio
import os
import ctypes
import json
import pathlib
import pywhatkit as pwk
import pyautogui
import pyperclip
from Backend.Model import close_any_app   # requires 'pywhatkit' installed and WhatsApp web logged in


def wait_for_window(title, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            try:
                windows[0].activate()
                time.sleep(1)
                return True
            except:
                pass
        time.sleep(0.5)
    return False

def focus_window(title):
    windows = gw.getWindowsWithTitle(title)
    if windows:
        try:
            windows[0].activate()
            time.sleep(1)
            return True
        except:
            return False
    return False


try:
    from pyttsx3 import init as tts_init
    engine = tts_init()
    def speak(text: str):
        engine.say(text)
        engine.runAndWait()
except Exception:
    def speak(text: str):
        """Fallback silent speak function"""
        pass

# -------------------------
# Config / env
# -------------------------
env = dotenv_values(".env")
GroqApiKey = env.get("GroqApiKey")

camera = None

classes = [
    "zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vlzY6d",
    "webanswers-webanswers_table__webanswers-table", "dDoNo ikb48b gsrt", "sXLaOe",
    "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"

client = Groq(api_key=GroqApiKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
    "Please let me know if there's anything more I can do to assist you; I'm here to help.",
    "If you have any further inquiries or require assistance, I'm just a message away.",
    "I'm committed to providing you with the best support possible, so please don't hesitate to contact me for any further help or questions."
]

messages = []

# Use env Username if set, otherwise fallback
USERNAME = os.environ.get("Username", "User")
SystemChatBot = [{"role": "system", "content": f"Hello, I am {USERNAME}, You're a Designer and Developer. Answer as concisely as possible."}]

# -------------------------
# Utilities & actions
# -------------------------
def GoogleSearch(Topic):
    search(Topic)
    return True


allowed_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg
}
# --- Windows hardware media keys ---
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1

def press_key(vk):
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk, 0, 2, 0)

def Content(Topic):
    def OpenNotepad(File):
        default_text_editor = "notepad.exe"
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=0.7,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            # robust attribute access for streaming chunks
            try:
                if getattr(chunk.choices[0].delta, "content", None):
                    Answer += chunk.choices[0].delta.content
            except Exception:
                # fallback dict-like
                try:
                    Answer += chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")  # type: ignore
                except Exception:
                    pass

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = str(Topic).replace("Content", "")
    ContentByAI = ContentWriterAI(Topic)

    data_path = pathlib.Path("Data")
    data_path.mkdir(parents=True, exist_ok=True)
    file_path = data_path / f"{Topic.lower().replace(' ', '')}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(str(file_path))
    return True

def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webopen(Url4Search)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def OpenApp(app):
    app = app.lower().strip()

    # ✅ HARD SYSTEM APPS (NO FUZZY MATCH)
    if app in ["notepad", "note pad"]:
        subprocess.Popen("notepad.exe")
        return "Notepad opened"

    if app in ["calculator", "calc"]:
        subprocess.Popen("calc.exe")
        return "Calculator opened"

    if app in ["file explorer", "explorer"]:
        subprocess.Popen("explorer.exe")
        return "File Explorer opened"

    if app in ["command prompt", "cmd"]:
        subprocess.Popen("cmd.exe")
        return "Command Prompt opened"

    # ✅ Websites
    if app in ["google", "google chrome", "chrome"]:
        webbrowser.open("https://www.google.com")
        return "Google opened"

    if app == "youtube":
        webbrowser.open("https://www.youtube.com")
        return "YouTube opened"

    if app in ["task manager"]:
        subprocess.Popen("taskmgr.exe")
        return "Task Manager opened"

    if app in ["powershell"]:
        subprocess.Popen("powershell.exe")
        return "PowerShell opened"
    
    if app in ["control panel", "control"]:
        subprocess.Popen("control.exe")
        return "Control Panel opened"
    
    if app in ["settings"]:
        subprocess.Popen("ms-settings:")
        return "Settings opened"
    
    if app in ["paint", "mspaint"]:
        subprocess.Popen("mspaint.exe")
        return "Paint opened"
    
    if app in ["wordpad"]:
        subprocess.Popen("wordpad.exe")
        return "WordPad opened"
    
    if app in ["snipping tool", "snip & sketch"]:
        subprocess.Popen("snippingtool.exe")
        return "Snipping Tool opened"
    
    # ✅ Registry Installed Apps
    registry_launch = launch_app(app)
    if registry_launch:
        return registry_launch


    # ✅ Fallback → AppOpener
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return f"{app} opened"
    except Exception:
        webbrowser.open(f"https://www.google.com/search?q={app}")
        return f"Searching {app} on Google"

def search_google(query):
        search_url = f"https://www.google.com/search?q={query}"

        try:
            resp = requests.get(search_url, headers={"User-Agent": useragent}, timeout=7)
            html = resp.text
        except Exception:
            return False

        links = []
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            # Google search result links often use '/url?q=<actual>&...'
            if href.startswith("/url?q="):
                url = href.split("/url?q=", 1)[1].split("&", 1)[0]
                url = requests.utils.unquote(url)
                if url.startswith("http"):
                    links.append(url)
            elif href.startswith("http"):
                links.append(href)

        if links:
            webopen(links[0])
            return True
        return False

def CloseApp(app):
    app = app.lower().strip()

    # 🔥 FIRST: try universal killer
    result = close_any_app(app)

    if result:
        return f"{app} closed"

    # 🔁 fallback to AppOpener
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return f"{app} closed"
    except Exception:
        return False
    
def System(command: str):
    command = command.lower().strip()

    if command in ("volume up", "increase volume"):
        press_key(VK_VOLUME_UP)
        return "Volume increased"

    if command in ("volume down", "decrease volume"):
        press_key(VK_VOLUME_DOWN)
        return "Volume decreased"

    if command in ("mute", "volume mute"):
        press_key(VK_VOLUME_MUTE)
        return "Volume muted"

    if command in ("unmute", "volume unmute"):
        press_key(VK_VOLUME_MUTE)  # toggle
        return "Volume unmuted"

    if command in ("play pause", "pause", "resume"):
        press_key(VK_MEDIA_PLAY_PAUSE)
        return "Media play/pause toggled"

    if command in ("next song", "next track"):
        press_key(VK_MEDIA_NEXT_TRACK)
        return "Next track"

    if command in ("previous song", "previous track"):
        press_key(VK_MEDIA_PREV_TRACK)
        return "Previous track"

    if command in ("close window", "close tab", "close this"):
        ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)  # ALT
        ctypes.windll.user32.keybd_event(0x73, 0, 0, 0)  # F4
        ctypes.windll.user32.keybd_event(0x73, 0, 2, 0)
        ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)
        return "Window closed"

    return False


# -------------------------
# Write code helper
# -------------------------
def WriteCodeInEditor(code_text: str, filename: str = "main.py", editor_cmd: str = "code"):
    """
    Writes `code_text` to Data/<filename> and opens it with `editor_cmd`.
    editor_cmd defaults to 'code' (VS Code CLI). Falls back to OpenApp(editor name).
    """
    try:
        data_path = pathlib.Path("Data")
        data_path.mkdir(parents=True, exist_ok=True)
        file_path = data_path / filename
        file_path.write_text(code_text, encoding="utf-8")
        # try to open using editor CLI (e.g., 'code' for VS Code)
        try:
            subprocess.Popen([editor_cmd, str(file_path)])
            return True
        except Exception:
            # fallback: try to open editor by name (uses your existing OpenApp)
            try:
                OpenApp(editor_cmd)
                return True
            except Exception:
                return False
    except Exception:
        return False

# -------------------------
# Contacts & WhatsApp helpers
# -------------------------
CONTACTS_PATH = pathlib.Path("Data") / "contacts.json"
CONTACTS_PATH.parent.mkdir(parents=True, exist_ok=True)

# create default contacts file with example if missing
if not CONTACTS_PATH.exists():
    default_contacts = {
        "Ankit Dubey": "+917307298260",   # <- replace with real number (include country code)
        # add more: "Alice": "+441234567890"
    }
    CONTACTS_PATH.write_text(json.dumps(default_contacts, indent=4), encoding="utf-8")

def load_contacts() -> dict:
    try:
        return json.loads(CONTACTS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def get_contact_number(name: str) -> str | None:
    if not name:
        return None
    contacts = load_contacts()
    for k, v in contacts.items():
        if k.lower() == name.strip().lower():
            return v
    for k, v in contacts.items():
        if name.strip().lower() in k.lower():
            return v
    return None

def prompt_for_message(recipient_name: str) -> str:
    """
    Try speech-first if SpeechRecognition() exists in globals; otherwise fallback to input().
    Returns the message text (or empty string).
    """
    if "SpeechRecognition" in globals() and callable(globals()["SpeechRecognition"]):
        try:
            spoken = globals()["SpeechRecognition"]()
            if spoken:
                return spoken
        except Exception:
            pass
    try:
        return input(f"What message should I send to {recipient_name}? ").strip()
    except Exception:
        return ""

def SendWhatsApp(recipient: str, message: str, wait_time: int = 3):
    """
    Send WhatsApp message instantly using pywhatkit.sendwhatmsg_instantly.
    recipient must be full phone number with country code like '+911234567890'.
    wait_time: seconds pywhatkit waits for browser/web to load (small delay).
    Returns True on success, False otherwise.
    """
    try:
        pwk.sendwhatmsg_instantly(recipient, message, wait_time=wait_time, tab_close=True, close_time=3)
        return True
    except Exception:
        return False
    
def WriteInActiveWindow(text):
    time.sleep(1)
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    return "Text written successfully."
# ==========================
# DESKTOP WHATSAPP CONTROL
# ==========================

def OpenWhatsAppDesktop():
    try:
        path = os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Local\WhatsApp\WhatsApp.exe")
        Application().start(path)
        time.sleep(5)
        return True
    except:
        subprocess.Popen("whatsapp:")
        time.sleep(5)
        return True


def FocusWhatsApp():
    windows = gw.getWindowsWithTitle("WhatsApp")
    if windows:
        windows[0].activate()
        time.sleep(1)
        return True
    return False


def SendWhatsAppDesktop(contact_name, message):
    try:
        subprocess.Popen("whatsapp:")

        if not wait_for_window("WhatsApp", 15):
            return "WhatsApp not opened"

        # 🔥 CORRECT SHORTCUT
        pyautogui.hotkey("ctrl", "k")
        time.sleep(1)

        pyperclip.copy(contact_name)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(2)

        pyautogui.press("enter")
        time.sleep(1)

        pyperclip.copy(message)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)

        pyautogui.press("enter")

        return f"Message sent to {contact_name}"

    except Exception as e:
        return f"WhatsApp failed: {e}"
    
    
# ==========================
# 🎥 CAMERA SYSTEM (FINAL)
# ==========================

camera = None
recording = False
video_writer = None


# =========================
# 🎥 OPEN CAMERA
# =========================
def open_camera():
    global camera

    if camera is not None:
        return "Camera already open"

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        camera = None
        return "Camera failed to open"

    return "Camera opened"


# =========================
# 📸 CLICK PHOTO
# =========================
def click_photo():
    global camera

    os.makedirs("Data/photos", exist_ok=True)

    # ✅ reuse camera or open new
    if camera is None:
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        time.sleep(1)

    if not camera.isOpened():
        return "Camera not available"

    # 🔥 warm-up
    frame = None
    for _ in range(30):
        ret, temp = camera.read()
        if ret:
            frame = temp
        time.sleep(0.02)

    if frame is None:
        camera.release()
        cv2.destroyAllWindows()
        camera = None
        return "Failed to capture photo"

    # 🔥 preview (nice UI)
    for _ in range(20):
        ret, temp = camera.read()
        if ret:
            cv2.imshow("Camera Preview", temp)
            cv2.waitKey(30)

    filename = f"Data/photos/photo_{int(time.time())}.jpg"
    cv2.imwrite(filename, frame)

    # ✅ IMPORTANT: release camera
    camera.release()
    cv2.destroyAllWindows()
    camera = None

    return "Photo captured successfully"


# =========================
# ❌ CLOSE CAMERA
# =========================
def close_camera():
    global camera

    if camera is not None:
        camera.release()
        cv2.destroyAllWindows()
        camera = None
        return "Camera closed"

    return "Camera already closed"


# =========================
# 🎥 START RECORDING
# =========================
def start_recording():
    global camera, recording, video_writer

    os.makedirs("Data/videos", exist_ok=True)

    if camera is None:
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        return "Camera failed"

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    filename = f"Data/videos/video_{int(time.time())}.avi"

    video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
    recording = True

    def record():
        global recording, camera, video_writer

        while recording:
            ret, frame = camera.read()
            if ret:
                video_writer.write(frame)
                cv2.imshow("Recording...", frame)

                if cv2.waitKey(1) & 0xFF == 27:
                    break

        # cleanup
        video_writer.release()
        camera.release()
        cv2.destroyAllWindows()

    threading.Thread(target=record).start()

    return "Recording started"


# =========================
# ⛔ STOP RECORDING
# =========================
def stop_recording():
    global recording

    if recording:
        recording = False
        return "Recording stopped and saved"

    return "No recording in progress"
    
    
# ==========================
# TAKE SCREENSHOT
# =========================

def take_screenshot():
    try:
        os.makedirs("Data/screenshots", exist_ok=True)

        filename = f"Data/screenshots/screenshot_{int(time.time())}.png"

        # 🔥 small delay (so user can prepare screen)
        time.sleep(0.5)

        screenshot = pyautogui.screenshot()
        screenshot.save(filename)

        return "Screenshot saved successfully"

    except Exception as e:
        return f"Screenshot failed: {e}"
# ==========================
# EMAIL AUTOMATION
# ==========================

def SendEmail(receiver, subject, body):
    try:
        sender = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASS")

        if not sender or not password:
            return "Email credentials not configured."

        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)

        return "Email sent successfully."

    except Exception as e:
        return f"Email failed: {e}"
# ==========================
# ALARM SYSTEM
# ==========================
def set_alarm(command):
    
    import winsound

    match = re.search(r"(\d{1,2}:\d{2})", command)

    if not match:
        return "Please specify time like 13:07"

    alarm_time = match.group(1)

    def alarm_thread():
        while True:
            current_time = time.strftime("%H:%M")
            if current_time == alarm_time:
                for _ in range(5):  # 🔥 ring 5 times
                    winsound.PlaySound("C:\\Windows\\Media\\Alarm01.wav", winsound.SND_FILENAME)
                    time.sleep(0.5)
                break
            time.sleep(10)
        print("⏰ Alarm ringing!")
    threading.Thread(target=alarm_thread, daemon=True).start()

    return f"Alarm set for {alarm_time}"

# ==========================
# ⏰ SMART REMINDER SYSTEM
# ==========================

def set_reminder(command):
    command = command.lower()

    # =========================
    # 🕒 TIME FORMAT (14:30)
    # =========================
    time_match = re.search(r"(\d{1,2}:\d{2})", command)

    if time_match:
        reminder_time = time_match.group(1)

        task = command.replace("remind me to", "")
        task = task.replace(f"at {reminder_time}", "").strip()

        def reminder_thread():
            while True:
                current = time.strftime("%H:%M")
                if current == reminder_time:
                    print(f"🔔 Reminder: {task}")

                    import winsound
                    for _ in range(3):
                        winsound.Beep(1000, 800)
                        time.sleep(0.5)

                    break
                time.sleep(5)

        threading.Thread(target=reminder_thread, daemon=True).start()

        return f"Reminder set for {reminder_time}"

    # =========================
    # ⏳ DELAY FORMAT (in minutes)
    # =========================
    delay_match = re.search(r"in (\d+) minute", command)

    if delay_match:
        minutes = int(delay_match.group(1))

        task = command.replace("remind me to", "")
        task = task.replace(f"in {minutes} minutes", "").strip()

        def reminder_thread():
            time.sleep(minutes * 60)

            print(f"🔔 Reminder: {task}")

            import winsound
            for _ in range(3):
                winsound.Beep(1000, 800)
                time.sleep(0.5)

        threading.Thread(target=reminder_thread, daemon=True).start()

        return f"Reminder set in {minutes} minutes"

    return "Could not understand reminder"

# ==========================
# CALCULATOR AUTOMATION
# ==========================

def calculate_expression(command: str):
    try:
        cmd = command.lower()

        cmd = cmd.replace("calculate", "")
        cmd = cmd.replace("into", "*")
        cmd = cmd.replace("x", "*")
        cmd = cmd.replace("multiply", "*")
        cmd = cmd.replace("plus", "+")
        cmd = cmd.replace("minus", "-")
        cmd = cmd.replace("divide", "/")

        expr = re.sub(r"[^0-9\.\+\-\*\/\(\)]", "", cmd)

        if not expr:
            return "Invalid expression"

        result = eval(expr, {"__builtins__": None}, {})

        # 🔥 If calculator window exists → type expression
        windows = gw.getWindowsWithTitle("Calculator")
        if windows:
            windows[0].activate()
            time.sleep(0.5)
            pyautogui.write(expr)
            pyautogui.press("enter")

        return f"The answer is {result}"

    except:
        return "Invalid expression"
    
def calculate_in_calculator(command: str):
    try:
        import re

        cmd = command.lower()

        cmd = cmd.replace("open calculator", "")
        cmd = cmd.replace("and", "")
        cmd = cmd.replace("calculate", "")

        cmd = cmd.replace("into", "*")
        cmd = cmd.replace("x", "*")
        cmd = cmd.replace("multiply", "*")
        cmd = cmd.replace("plus", "+")
        cmd = cmd.replace("minus", "-")
        cmd = cmd.replace("divide", "/")

        expr = re.sub(r"[^0-9\+\-\*\/]", "", cmd)

        if not expr:
            return "Invalid expression"

        subprocess.Popen("calc.exe")

        # 🔥 USE THIS INSTEAD OF sleep
        if wait_for_window("Calculator"):
            pyautogui.write(expr, interval=0.1)
            pyautogui.press("enter")

        return f"Calculated {expr} in calculator"

    except Exception as e:
        return f"Calculator automation failed: {e}"
# -------------------------
# Main translate & execute (replaced/cleaned block)
# -------------------------
async def TranslateAndExecute(commands: list[str]):
    """
    Execute a list of command strings by dispatching to background threads.
    Returns a list of results (in same order as commands).
    """
    tasks = []

    for command in commands:
        cmd = command.strip()
        low = cmd.lower()
        
# ===============================
# WHATSAPP FULL COMMAND PARSER
# ===============================
        if "whatsapp" in low and "send" in low:

            try:
                # Normalize text
                text = command.lower()

                # Extract name + message
                match = re.search(
                    r"(?:send message to|send|whatsapp)\s+(.+?)\s+(.*)",
                    command,
                    re.IGNORECASE
                )

                if match:
                    contact = match.group(1).strip()
                    message = match.group(2).strip()

                    tasks.append(asyncio.to_thread(SendWhatsAppDesktop, contact, message))
                else:
                    tasks.append(asyncio.to_thread(lambda: "Could not understand contact or message"))

            except Exception as e:
                tasks.append(asyncio.to_thread(lambda e: f"WhatsApp failed: {e}", e))
                
# ===============================
# APPLICATION COMMANDS
# ===============================
        elif low.startswith("open "):
            target = cmd[len("open "):].strip()
            if target:
                tasks.append(asyncio.to_thread(OpenApp, target))
            else:
                tasks.append(asyncio.to_thread(lambda: False))

        elif low.startswith("close "):
            target = cmd[len("close "):].strip()
            tasks.append(asyncio.to_thread(CloseApp, target))


        elif low.startswith("force close "):
            target = cmd[len("force close "):].strip()
            tasks.append(asyncio.to_thread(CloseApp, target))

        elif low.startswith("play "):
            target = cmd[len("play "):].strip()
            if target:
                tasks.append(asyncio.to_thread(PlayYoutube, target))
            else:
                tasks.append(asyncio.to_thread(lambda: False))

        elif low.startswith("content "):
            target = cmd[len("content "):].strip()
            if target:
                tasks.append(asyncio.to_thread(Content, target))
            else:
                tasks.append(asyncio.to_thread(lambda: False))

        elif low.startswith("google search "):
            target = cmd[len("google search "):].strip()
            tasks.append(asyncio.to_thread(search_google, target))

        elif low.startswith("youtube search "):
            target = cmd[len("youtube search "):].strip()
            tasks.append(asyncio.to_thread(YouTubeSearch, target))

        elif low.startswith("system "):
            target = cmd[len("system "):].strip()
            tasks.append(asyncio.to_thread(System, target))
        elif low in ("volume up", "increase volume"):
            tasks.append(asyncio.to_thread(System, "volume up"))

        elif low in ("volume down", "decrease volume"):
            tasks.append(asyncio.to_thread(System, "volume down"))

        elif low in ("mute", "volume mute"):
            tasks.append(asyncio.to_thread(System, "mute"))

        elif low in ("unmute", "volume unmute"):
            tasks.append(asyncio.to_thread(System, "unmute"))

        elif low.startswith("generate image"):
             # let Main.py handle it, do nothing here
            tasks.append(asyncio.to_thread(lambda: True))
        
        elif low.startswith("write "):
            text = cmd.replace("write", "").strip()
            tasks.append(asyncio.to_thread(WriteInActiveWindow, text))

        elif low.startswith("press "):
            key = cmd.replace("press", "").strip()
            tasks.append(asyncio.to_thread(pyautogui.press, key))
            
        elif "open camera" in low:
            tasks.append(asyncio.to_thread(open_camera))
        
        elif any(x in low for x in ["take screenshot", "take a screenshot", "screenshot"]):
            tasks.append(asyncio.to_thread(take_screenshot))

        elif any(x in low for x in ["click photo", "click my photo", "take photo", "take my photo"]):
            tasks.append(asyncio.to_thread(click_photo))

        elif "close camera" in low:
            tasks.append(asyncio.to_thread(close_camera))

        elif "start recording" in low:
            tasks.append(asyncio.to_thread(start_recording))

        elif "stop recording" in low:
            tasks.append(asyncio.to_thread(stop_recording))
            
        elif "close camera" in low:
            tasks.append(asyncio.to_thread(close_camera))

        elif "set alarm" in low:
            tasks.append(asyncio.to_thread(set_alarm, cmd))
        
        elif "remind me" in low:
            tasks.append(asyncio.to_thread(set_reminder, cmd))
                    

        elif "write code" in low or "create code" in low:
            # keep previous logic for extracting code + filename + editor
            payload = cmd
            code_part = None
            filename = "main.py"
            editor_cmd = "code"

            for sep in [":", "->", "|"]:
                if sep in payload:
                    left, right = payload.split(sep, 1)
                    code_part = right.strip()
                    if ".py" in left or ".js" in left or ".java" in left:
                        for token in left.split():
                            if token.endswith((".py", ".js", ".java", ".ts", ".cpp")):
                                filename = token
                                break
                    break

            if not code_part:
                for kw in ("write code", "write", "create code", "create"):
                    if payload.lower().startswith(kw):
                        code_part = payload[len(kw):].strip()
                        break

            if not code_part:
                code_part = "print('Hello World')"

            if "vscode" in payload.lower() or "vs code" in payload.lower():
                editor_cmd = "code"
            else:
                for ed in ("sublime", "notepad++", "notepad", "atom", "pycharm", "vscode", "vs code"):
                    if ed in payload.lower():
                        editor_cmd = ed
                        break

            tasks.append(asyncio.to_thread(WriteCodeInEditor, code_part, filename, editor_cmd))
            
        elif low.startswith("email"):
            # format: email receiver|subject|body
            parts = cmd.replace("email", "").strip().split("|")

            if len(parts) == 3:
                tasks.append(asyncio.to_thread(SendEmail, parts[0], parts[1], parts[2]))
            else:
                tasks.append(asyncio.to_thread(lambda: False))
                      
        
        elif "open calculator" in low and "calculate" in low:
            tasks.append(asyncio.to_thread(calculate_in_calculator, cmd))

        elif "calculate" in low:
            tasks.append(asyncio.to_thread(calculate_expression, cmd))
                    
 

        else:
            # Unknown / unhandled command: return False or placeholder
            tasks.append(asyncio.to_thread(lambda: False))

    # gather results and return
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=False)
    else:
        results = []
    return results

async def Automation(commands: list[str]):
    try:
        results = await TranslateAndExecute(commands)

        # remove None results
        cleaned = [r for r in results if r]

        return cleaned if cleaned else ["Done"]

    except Exception as e:
        print("Automation engine error:", e)
        return ["Automation failed"]

# =====================================================
# AI CODE GENERATION + LANGUAGE DETECTION (ADD-ON)
# =====================================================

def DetectLanguage(code: str) -> str:
    code = code.strip()

    if code.startswith("import ") or "def " in code or "print(" in code:
        return "python"
    if "console.log" in code or "function " in code or "=>" in code:
        return "javascript"
    if "#include" in code or "int main" in code:
        return "cpp"
    if "public static void main" in code:
        return "java"

    return "text"

# This function maps detected language to a folder path, creates the folder if it doesn't exist, and returns the path.
def ResolveCodeFolder(language: str) -> pathlib.Path:
    base = pathlib.Path("GeneratedCode")

    mapping = {
        "python": base / "Python",
        "javascript": base / "JavaScript",
        "cpp": base / "CPP",
        "java": base / "Java",
        "text": base / "Other"
    }

    folder = mapping.get(language, base / "Other")
    folder.mkdir(parents=True, exist_ok=True)
    return folder

# This function generates code using Groq AI based on a prompt, detects the programming language, and saves the code in the appropriate folder.
def GenerateAndSaveCode(prompt: str):
    """
    Generates code using Groq AI,
    detects language automatically,
    saves it into the correct folder.
    """

    messages.append({
        "role": "user",
        "content": f"Write clean production-ready code:\n{prompt}"
    })

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=SystemChatBot + messages,
        max_tokens=2048,
        temperature=0.4
    )

    code = completion.choices[0].message.content.strip()
    language = DetectLanguage(code)
    folder = ResolveCodeFolder(language)

    ext_map = {
        "python": ".py",
        "javascript": ".js",
        "cpp": ".cpp",
        "java": ".java",
        "text": ".txt"
    }

    filename = f"ai_generated{ext_map.get(language, '.txt')}"
    file_path = folder / filename
    file_path.write_text(code, encoding="utf-8")

    return {
        "language": language,
        "file": str(file_path),
        "code": code
    }

# -------------------------
# If run as script, run nothing by default (safe)
# -------------------------
if __name__ == "__main__":
    try:
        # Example test call (uncomment to test)
        # asyncio.run(Automation(["send whatsapp to Ankit"]))
        asyncio.run(Automation([]))
    except KeyboardInterrupt:
        pass

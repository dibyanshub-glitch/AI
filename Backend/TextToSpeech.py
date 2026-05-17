# Backend/TextToSpeech.py
import os
import queue
import threading
import random
import pyttsx3
import eel
import asyncio
import edge_tts
import tempfile
import playsound
import pygame

from Backend import state
# -------------------------------------------------
# GLOBAL STOP FLAG (FOR BARGE-IN)
# -------------------------------------------------
STOP_TTS = False
# -------------------------------------------------
# SPEECH QUEUE (PREVENT OVERLAP)
# -------------------------------------------------
_tts_queue = queue.Queue()
_worker_started = False
_worker_lock = threading.Lock()

# def TExtToSpeech(text):
#     print("🔊 SPEAKING:", text)
def stop_tts_immediately():
    """Force stop current speech (barge-in)"""
    global STOP_TTS
    STOP_TTS = True

    try:
        pygame.mixer.music.stop()
    except:
        pass
# -------------------------------------------------
# CLEAN TEXT
# -------------------------------------------------
def _clean_text(text: str) -> str:
    return (
        text.replace("\n", " ")
            .replace("`", "")
            .replace("*", "")
            .replace("#", "")
            .replace("\\", "/")
            .strip()
    )

# -------------------------------------------------
# OFFLINE MALE TTS (ONLY ENGINE USED)
# -------------------------------------------------
def _offline_male_tts(text: str) -> bool:
    try:
        engine = pyttsx3.init()
        import random

        rate = random.randint(155, 178)
        engine.setProperty("rate", rate)

        # 🔥 FORCE MALE VOICE
        voices = engine.getProperty("voices")
        selected_voice = None

        for v in voices:
            name = v.name.lower()
            if "male" in name or "david" in name or "mark" in name:
                selected_voice = v.id
                break
        if hasattr(state, "VOICE_TYPE"):
            if state.VOICE_TYPE == "female":
                # select female voice
                pass
            else:
                # select male voice
                pass
        # Fallback: first available voice (still offline)
        if selected_voice:
            engine.setProperty("voice", selected_voice)

        engine.say(text)
        engine.runAndWait()
        return True

    except Exception as e:
        print("[TTS] Offline male TTS failed:", e)
        return False

# -------------------------------------------------
# CORE SPEAK FUNCTION (MALE ONLY)
# -------------------------------------------------
def _speak(text: str):
    text = _clean_text(text)
    if not text:
        return
    _offline_male_tts(text)

# -------------------------------------------------
# BACKGROUND WORKER THREAD
# -------------------------------------------------
def _tts_worker():
    while True:
        text = _tts_queue.get()

        # 🔥 TELL FRONTEND: Lukas started speaking
        try:
            eel.lukasSetSpeaking(True)
        except:
            pass

        # try ultra-real voice first
        try:
            asyncio.run(_edge_tts_speak(text))
        except:
            _speak(text)  # fallback to pyttsx3
        # 🔥 TELL FRONTEND: Lukas finished speaking
        try:
            eel.lukasSetSpeaking(False)
        except:
            pass

        _tts_queue.task_done()

def _ensure_worker():
    global _worker_started
    with _worker_lock:
        if not _worker_started:
            threading.Thread(target=_tts_worker, daemon=True).start()
            _worker_started = True

# -------------------------------------------------
# PUBLIC API (USED EVERYWHERE)
# -------------------------------------------------
def TTS(text: str) -> bool:
    if not text or not text.strip():
        return False

    _ensure_worker()
    _tts_queue.put(text)
    return True

# -------------------------------------------------
# SMART LONG-TEXT HANDLER (UNCHANGED BEHAVIOR)
# -------------------------------------------------
Responses = [
    "The rest of the response is available on the screen.",
    "Please check the screen for the remaining information.",
    "I've displayed the complete response on the screen.",
    "The rest of the answer is shown on the chat screen.",
    "I've provided the full response on the screen for you to read.",
    "The remaining details are visible on the screen.",
    "Please refer to the screen for the complete response."
    
]

def TExtToSpeech(full_text: str) -> bool:
    if not full_text:
        return False

    sentences = [
        s.strip()
        for s in full_text.replace("?", ".").replace("!", ".").split(".")
        if s.strip()
    ]

    # Long text → speak short + notify
    if len(full_text) >= 250 and len(sentences) > 4:
        short_text = ". ".join(sentences[:2]) + ". " + random.choice(Responses)
        return TTS(short_text)

    return TTS(full_text)

VOICE_POOL = [
    # "en-IN-PrabhatNeural",
    "en-US-GuyNeural",
     "en-GB-RyanNeural",
]

async def _edge_tts_speak(text: str):
    try:
        voice = random.choice(VOICE_POOL)

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            temp_path = f.name

        await communicate.save(temp_path)

        # ⭐ USE SAFE PLAYER (NOT playsound)
        # ✅ PRO AUDIO PLAYER
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()

        global STOP_TTS
        STOP_TTS = False

        while pygame.mixer.music.get_busy():

            # 🚨 HARD BARGE-IN CHECK
            if STOP_TTS:
                print("⚡ TTS INTERRUPTED")

                try:
                    pygame.mixer.music.stop()
                except:
                    pass

                break

        await asyncio.sleep(0.03)

        try:
            os.remove(temp_path)
        except:
            pass

        return True

    except Exception as e:
        print("Edge TTS failed:", e)
        return False
# -------------------------------------------------
# CLI TEST
# -------------------------------------------------
if __name__ == "__main__":
    print("Male-Only TTS Test (Offline, Stable)")
    try:
        while True:
            txt = input("Enter text: ").strip()
            if not txt:
                continue
            TExtToSpeech(txt)
    except KeyboardInterrupt:
        print("\nExiting.")

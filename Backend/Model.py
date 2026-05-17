# Model.py - defensive debug-friendly version


import inspect
import re
import time
import traceback
from click import prompt
from dotenv import dotenv_values
import psutil
from rich import print
import cohere
import ctypes

# --- Windows hardware volume keys ---
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF

def press_key(vk):
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk, 0, 2, 0)

# --------- Config ----------
MODEL_CHOICES = [
    "command-a-03-2025",
    "command-r-08-2024",
    "command-r7b-12-2024",
    "command-r-plus-08-2024"
]

# load API key
env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey") or env_vars.get("COHERE_API_KEY") or None
if not CohereAPIKey:
    print("[red]ERROR:[/red] CohereAPIKey not found in .env. Make sure `.env` has CohereAPIKey=<key> or set env var COHERE_API_KEY.")
cohere_client = None
try:
    cohere_client = cohere.Client(api_key=CohereAPIKey)
except Exception as e:
    print("[red]Failed to construct Cohere client:[/red]", e)
    traceback.print_exc()

# best-effort import of NotFoundError class
NotFoundError = None
try:
    from cohere.errors.not_found_error import NotFoundError as _NF
    NotFoundError = _NF
except Exception:
    try:
        from cohere.errors import NotFoundError as _NF2
        NotFoundError = _NF2
    except Exception:
        NotFoundError = None

# -------------------------
funcs = [
    "exit", "general", "realtime", "open", "close", "play", "generate image",
    "system", "content", "google search", "youtube search", "wikipedia search", "reminder",
    "joke", "quote", "advice", "weather", "news", "translate", "define", "synonym", "antonym",
    "spell check", "grammar check", "summarize", "analyze sentiment", "classify", "recommend", "calculate", "convert", "compare", "time", "date", "timer", "alarm"  
]

_raw_ChatHistory = [
    {"role":"User","message":"Hello! Who are you?"},
    {"role":"Chatbot:","message":"general how are you?"},
    {"role":"User","message":"Can you tell me a joke?"},
    {"role":"Chatbot:","message":"Sure! Why did the scarecrow win an award? Because he was outstanding in his field!"},
    
    # ... (trimmed for brevity)
]

def normalize_chat_history(raw_history):
    normalized = []
    for entry in raw_history:
        role_raw = entry.get("role","")
        r = role_raw.strip().lower()
        if r.startswith("user"):
            role = "user"
        elif r.startswith("chatbot") or r.startswith("assistant"):
            role = "assistant"
        else:
            role = "user"
        content = entry.get("content") or entry.get("message") or ""
        normalized.append({"role": role, "content": content})
    return normalized

ChatHistory = normalize_chat_history(_raw_ChatHistory)

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'joke' if the user is asking for a joke like 'tell me a joke', 'can you joke about programmers?', etc.
-> Respond with 'quote' if the user is asking for a quote like 'tell me a quote', 'can you quote albert einstein?', etc.
-> Respond with 'advice' if the user is asking for advice like 'can you give me some advice on studying?', 'i need some advice on cooking.', etc.
-> Respond with 'weather (location)' if the user is asking about weather of any location like 'what's the weather in delhi?', 'tell me the weather of new york', etc.
-> Respond with 'news (topic)' if the user is asking about news of any topic like 'what's the news on coronavirus?', 'tell me news about space exploration', etc.
-> Respond with 'translate (text) to (language)' if the user is asking to translate any text to any language like 'translate hello to spanish', 'can you translate i love programming to french?', etc.
-> Respond with 'define (word)' if the user is asking to define any word like 'define serendipity', 'what's the meaning of ephemeral?', etc.
-> Respond with 'synonym (word)' if the user is asking for synonym of any word like 'what's the synonym of happy?', 'can you give me synonyms of fast?', etc.
-> Respond with 'antonym (word)' if the user is asking for antonym of any word like 'what's the antonym of good?', 'can you give me antonyms of hot?', etc.
-> Respond with 'spell check (sentence)' if the user is asking to spell check any sentence like 'can you spell check this sentence: i havv a speling eror?', 'spell check the sentence: this sentense has a mistake.', etc.
-> Respond with 'grammar check (sentence)' if the user is asking to grammar check any sentence like 'can you grammar check this sentence: she go to school everyday?', 'grammar check the sentence: he don't like pizza.', etc.
-> Respond with 'summarize (text)' if the user is asking to summarize any text like 'can you summarize the article about climate change?', 'summarize the text: Artificial Intelligence is transforming the world in many ways...', etc.
-> Respond with 'analyze sentiment (text)' if the user is asking to analyze sentiment of any text like 'can you analyze sentiment of this review: The movie was fantastic and I loved it!', 'analyze sentiment of the text: I am feeling sad today.', etc.
-> Respond with 'classify (text)' if the user is asking to classify any text like 'can you classify this email: "Congratulations! You've won a free cruise. Click here to claim."', 'classify the text: "I need help with my order, it's not working."', etc.
-> Respond with 'recommend (query)' if the user is asking for any recommendation like 'can you recommend a good book to read?', 'i need a recommendation for a new laptop.', etc.
-> Respond with 'calculate (query)' if the user is asking to calculate anything like 'can you calculate 25 multiplied by 4?', 'what's the result of 15 divided by 3?', etc.
-> Respond with 'convert (query)' if the user is asking to convert any unit or currency like 'can you convert 100 dollars to euros?', 'convert 5 kilometers to miles.', etc.
-> Respond with 'compare (query)' if the user is asking to compare two or more things like 'can you compare iphone 12 and samsung galaxy s21?', 'compare the cost of living in new york and san francisco.', etc.   
-> Respond with 'time (query)' if the user is asking about time, date, day, month, year, etc like 'what's the time?', 'what's today's date?', 'what day is it today?', 'what month are we in?', 'what year is it?', etc.    
-> Respond with 'timer (duration)' if the user is asking to set a timer like 'set a timer for 10 minutes', 'can you start a timer for 30 seconds?', etc.
-> Respond with 'alarm (datetime with message)' if a query is requesting to set a alarm like 'set an alarm at 7:00am tomorrow for my morning workout.' respond with 'alarm 7:00am tomorrow morning workout'.
-> Respond with 'wikipedia search (query)' if a query is asking to search any topic on wikipedia like 'can you search quantum physics on wikipedia?', 'wikipedia search history of india', etc.
-> Respond with 'exit' if the user is saying goodbye or wants to end the conversation like 'bye jarvis.', 'goodbye', 'see you later', etc.
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
-> Respond with 'content (topic)' if user asks to write code, script, application, or content for any program like notepad, vscode, word etc.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""
# -------------------------
def parse_response_text_to_tasks(text: str):
    if not text:
        return []
    t = re.sub(r'\s+', ' ', text.replace('\n',' ')).strip()
    parts = [p.strip() for p in t.split(',') if p.strip()]
    cleaned = []
    for p in parts:
        low = p.lower()
        matched = False
        for kw in sorted(funcs, key=lambda x: -len(x)):
            if low.startswith(kw):
                rest = p[len(kw):].strip()
                cleaned.append(f"{kw}{(' ' + rest) if rest else ''}".strip())
                matched = True
                break
        if not matched:
            cleaned.append(p)
    seen = set()
    res = []
    for it in cleaned:
        if it not in seen:
            seen.add(it)
            res.append(it)
    return res

# -------------------------
def _make_modern_messages(prompt_text):
    return [{"role":"user","content":prompt_text}]

def _make_legacy_message_and_history(prompt_text, chat_history):
    legacy_history = []
    for m in chat_history:
        role = m.get("role","user").upper()
        if role == "ASSISTANT":
            role = "CHATBOT"
        text = m.get("content") or m.get("message") or ""
        legacy_history.append({"role": role, "message": text})
    return prompt_text, legacy_history

def _collect_text_from_stream(stream):
    chunks=[]
    for event in stream:
        text_piece = ""
        try:
            if hasattr(event,"event_type") and getattr(event,"event_type")=="text_generation":
                text_piece = getattr(event,"text","") or ""
            else:
                text_piece = getattr(event,"text","") or ""
        except Exception:
            text_piece = ""
        if not text_piece and isinstance(event, dict):
            text_piece = event.get("text") or event.get("content") or event.get("message") or ""
        if text_piece:
            chunks.append(text_piece)
    return "".join(chunks)

def debug_cohere_signature():
    try:
        version = getattr(cohere, "__version__", "unknown")
        sig = inspect.signature(cohere_client.chat_stream)
        print("[green]cohere.__version__:[/green]", version)
        print("[green]chat_stream signature:[/green]", sig)
    except Exception as e:
        print("[red]Could not inspect signature:[/red]", e)
        traceback.print_exc()

# -------------------------
def _open_stream_with_fallback(stream_kwargs):
    if cohere_client is None:
        raise RuntimeError("cohere_client not initialized (missing API key or client construction failed).")
    last_exc = None
    for model_name in MODEL_CHOICES:
        try:
            print(f"[cyan]Attempting model:[/cyan] {model_name}")
            stream = cohere_client.chat_stream(model=model_name, **stream_kwargs)
            print(f"[green]Success with model:[/green] {model_name}")
            return stream
        except Exception as e:
            print(f"[yellow]Model attempt failed ({model_name}):[/yellow] {e}")
            traceback.print_exc()
            # If NotFoundError class is available, check instance
            if NotFoundError is not None and isinstance(e, NotFoundError):
                last_exc = e
                continue
            # fallback inspect message
            msg = str(e).lower()
            if "removed" in msg or "not found" in msg or "404" in msg:
                last_exc = e
                continue
            # If TypeError (signature mismatch), raise immediately so caller can adapt
            if isinstance(e, TypeError):
                raise
            last_exc = e
            continue
    if last_exc:
        raise last_exc
    raise RuntimeError("No models tried or unknown failure in _open_stream_with_fallback.")

# -------------------------
def FirstLayerDMM(prompt_text="test", max_retries=2):
    try:
        modern_messages = _make_modern_messages(prompt_text)
        legacy_message, legacy_chat_history = _make_legacy_message_and_history(prompt_text, ChatHistory)
        # inspect signature
        sig=None
        try:
            sig = inspect.signature(cohere_client.chat_stream)
        except Exception:
            try:
                sig = inspect.signature(cohere.Client.chat_stream)
            except Exception:
                sig=None
        # prepare kwargs accordingly
        if sig and 'messages' in sig.parameters:
            stream_kwargs = dict(
                messages=modern_messages,
                temperature=0.7,
                chat_history=ChatHistory,
                prompt_truncation='OFF',
                connectors=[],
                preamble=preamble
            )
        else:
            stream_kwargs = dict(
                message=legacy_message,
                chat_history=legacy_chat_history,
                temperature=0.7,
                prompt_truncation='OFF',
                preamble=preamble
            )
        # open stream with fallback
        stream = _open_stream_with_fallback(stream_kwargs)
        # collect text
        try:
         response_text = _collect_text_from_stream(stream)
        except Exception:
            return ["general " + prompt_text]

        if not response_text:
            return []
        tasks = parse_response_text_to_tasks(response_text)
        if any("(query)" in t.lower() for t in tasks) and max_retries>0:
            time.sleep(0.2)
            return FirstLayerDMM(prompt_text=prompt_text, max_retries=max_retries-1)
        return tasks
     
        
    except Exception as e:
        print("[red]Exception in FirstLayerDMM:[/red]", e)
        traceback.print_exc()
        return []

def System(command: str):
    command = command.lower().strip()

    if command in ("volume up", "increase volume"):
        press_key(VK_VOLUME_UP)
        return True

    if command in ("volume down", "decrease volume"):
        press_key(VK_VOLUME_DOWN)
        return True

    if command in ("mute", "volume mute"):
        press_key(VK_VOLUME_MUTE)
        return True

    if command in ("unmute","volume unmute"):
        press_key(VK_VOLUME_MUTE)  # toggle
        return True

    return False

# =====================================================
# UNIVERSAL APP CLOSER (JARVIS LEVEL)
# =====================================================

def close_any_app(app_name: str):
    """
    Attempts to close any running application by matching process names.
    Much more reliable than AppOpener.close().
    """

    if not app_name:
        return False

    app_name = app_name.lower().replace(".exe", "").strip()

    killed = False

    try:
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pname = proc.info["name"].lower()

                # remove .exe for matching
                pname_clean = pname.replace(".exe", "")

                # 🔥 SMART MATCH
                if (
                    app_name in pname_clean
                    or pname_clean in app_name
                ):
                    print(f"🛑 Killing process: {pname}")
                    proc.kill()
                    killed = True

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return killed

    except Exception as e:
        print("Close-any error:", e)
        return False
# -------------------------
if __name__ == "__main__":
    print("[cyan]FirstLayerDMM - debug-friendly wrapper[/cyan]")
    print("Type messages. Type 'debug' to print cohere signature. Ctrl+C to exit.")
    try:
        while True:
            user_input = prompt(">>> ")
            if not user_input:
                continue
            if user_input.strip().lower() == "debug":
                debug_cohere_signature()
                continue
            result = FirstLayerDMM(user_input)
            print("[magenta]Result:[/magenta]", result)
    except KeyboardInterrupt:
        print("\n[red]Bye[/red]")

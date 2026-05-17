# voice_recognition.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
from pathlib import Path
import os
import time
import mtranslate as mt

# ---- config / env ----
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")  # default to English
# Temp dir for assistant status & files
current_dir = Path.cwd()
TempDirPath = current_dir / "Frontend" / "Files"
DataDir = current_dir / "Data"
TempDirPath.mkdir(parents=True, exist_ok=True)
DataDir.mkdir(parents=True, exist_ok=True)

# ---- prepare HTML (use correct spacing and output id) ----
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            // prefer webkitSpeechRecognition when available
            recognition = (window.webkitSpeechRecognition ? new webkitSpeechRecognition() : new (window.SpeechRecognition || window.webkitSpeechRecognition)());
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent = output.textContent + transcript;
            };

            recognition.onend = function() {
                // do not automatically restart if stopped by user
            };
            recognition.start();
        }

        function stopRecognition() {
            if (recognition) {
                recognition.stop();
            }
        }
    </script>
</body>
</html>'''

# insert InputLanguage into the JS
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# write HTML file
voice_html_path = DataDir / "Voice.html"
voice_html_path.write_text(HtmlCode, encoding="utf-8")

# file:// URI
Link = voice_html_path.as_uri()

# ---- Chrome / Selenium setup ----
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
chrome_options.add_argument(f'--user-agent={user_agent}')
# Use fake media stream / devices so tests can run headless. If you want real mic, remove these.
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
# Headless newer option may be different; use classic headless for compatibility
chrome_options.add_argument("--headless=new")  # if problematic, change to "--headless"
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# ---- helper functions ----
def SetAssistantStatus(Status: str):
    try:
        status_file = TempDirPath / "Status.data"
        status_file.write_text(Status, encoding="utf-8")
    except Exception as e:
        print("Failed to write status:", e)

def QueryModifier(Query: str) -> str:
    """
    Normalize punctuation: if the query looks like a question (has wh-words or starts with auxiliary),
    make sure it ends with '?', otherwise end with '.'.
    Capitalize first letter.
    """
    if not Query:
        return ""

    q = Query.strip()
    q = " ".join(q.split())  # collapse whitespace
    q_lower = q.lower()

    question_starters = {
        "who", "what", "when", "where", "why", "how",
        "is", "are", "do", "does", "did", "can", "could", "would", "should", "will", "whom", "whose"
    }

    # check if first word is a question word or auxiliary
    first_word = q_lower.split()[0]
    is_question = first_word in question_starters or any(q_lower.startswith(w + " ") for w in ("can", "could", "would", "should", "will"))

    # ensure single trailing punctuation
    if q[-1] in ".!?":
        q = q[:-1]

    q = q + ("?" if is_question else ".")
    return q[0].upper() + q[1:]

def UniversalTranslator(Text: str) -> str:
    if not Text:
        return ""
    try:
        english_translation = mt.translate(Text, "en", "auto")
        return english_translation.capitalize()
    except Exception as e:
        print("Translation failed:", e)
        return Text

# ---- main recognition routine ----
def SpeechRecognition(timeout_seconds: int = 20, poll_interval: float = 0.5) -> str:
    """
    Opens the local HTML page, starts recognition, polls the output element until non-empty
    or timeout. Stops recognition and returns the (possibly translated & normalized) query.
    """
    driver.get(Link)

    # click start button
    try:
        start_btn = driver.find_element(By.ID, "start")
        start_btn.click()
    except Exception as e:
        print("Failed to click start button:", e)
        return ""

    start_time = time.time()
    captured_text = ""

    # poll for content in the <p id="output">
    while True:
        try:
            output_elem = driver.find_element(By.ID, "output")  # lowercase id
            Text = output_elem.text or output_elem.get_attribute("textContent") or ""
            if Text and Text.strip():
                captured_text = Text.strip()
                # stop recognition by clicking end button (graceful)
                try:
                    end_btn = driver.find_element(By.ID, "end")
                    end_btn.click()
                except Exception:
                    # as fallback attempt to execute stopRecognition via JS
                    try:
                        driver.execute_script("if(window.recognition){ window.recognition.stop(); }")
                    except Exception:
                        pass
                break

            if time.time() - start_time > timeout_seconds:
                # timeout: stop recognition and return empty string
                try:
                    driver.execute_script("if(window.recognition){ window.recognition.stop(); }")
                except Exception:
                    pass
                break

        except Exception as e:
            # element not present yet; just wait a bit
            # print("Polling error:", e)  # uncomment for debugging
            pass

        time.sleep(poll_interval)

    if not captured_text:
        return ""

    # If input language is English (or contains 'en'), skip translation; else translate
    if InputLanguage and ("en" == InputLanguage.lower() or "en" in InputLanguage.lower()):
        return QueryModifier(captured_text)
    else:
        SetAssistantStatus("Translating...")
        translated = UniversalTranslator(captured_text)
        return QueryModifier(translated)

# ---- run loop ----
if __name__ == "__main__":
    try:
        while True:
            recognized = SpeechRecognition(timeout_seconds=25, poll_interval=0.5)
            if recognized:
                print("Recognized Text:", recognized)
            else:
                print("No speech detected or timed out.")
            time.sleep(0.5)  # small pause before next iteration
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        try:
            driver.quit()
        except Exception:
            pass

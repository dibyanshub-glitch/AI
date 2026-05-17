import pyttsx3

def startup_greeting():
    engine = pyttsx3.init()
    engine.say("Hello sir, welcome")
    engine.runAndWait()

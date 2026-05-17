import speech_recognition as sr

def listen_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        return r.recognize_google(audio).lower()
    except:
        return ""

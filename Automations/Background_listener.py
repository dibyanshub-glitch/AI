import speech_recognition as sr
import wave
import os

def listen_forever():
    r = sr.Recognizer()
    os.makedirs("Data", exist_ok=True)

    with sr.Microphone(sample_rate=16000) as source:
        r.adjust_for_ambient_noise(source)

        while True:
            print("🎧 Listening...")
            audio = r.listen(source)

            # ✅ Save live voice correctly
            with wave.open("Data/live_voice.wav", "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)       # 16-bit
                wf.setframerate(16000)
                wf.writeframes(audio.get_raw_data())

            try:
                text = r.recognize_google(audio).lower()
                print("🗣️ Heard:", text)
                yield text
            except Exception:
                continue

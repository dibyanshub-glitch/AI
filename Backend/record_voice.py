import speech_recognition as sr
import wave

def record_voice(filename="Data/live_voice.wav", seconds=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Speak now...")
        audio = r.listen(source, timeout=seconds)

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio.get_raw_data())

    print(f"✅ Voice recorded: {filename}")

if __name__ == "__main__":
    record_voice()

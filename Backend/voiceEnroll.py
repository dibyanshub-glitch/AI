import os
import json
import shutil

VOICE_DIR = "Data/voices"
DB_PATH = "Data/voice_db.json"

os.makedirs(VOICE_DIR, exist_ok=True)

def enroll_voice(username, wav_path):
    if not os.path.exists(wav_path):
        print("❌ WAV file not found:", wav_path)
        return False

    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            db = json.load(f)
    else:
        db = {}

    user_files = db.get(username, [])
    new_name = f"{username}_{len(user_files)+1}.wav"
    dest = os.path.join(VOICE_DIR, new_name)

    shutil.copy(wav_path, dest)

    user_files.append(new_name)
    db[username] = user_files

    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

    print(f"✅ Voice enrolled for {username}")
    return True


# 🧪 TEST RUN
if __name__ == "__main__":
    enroll_voice("ankit", "Data/live_voice.wav")

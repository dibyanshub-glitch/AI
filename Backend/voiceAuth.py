import os
import json
import numpy as np
import librosa
from scipy.spatial.distance import cosine

VOICE_DIR = "Data/voices"
DB_PATH = "Data/voice_db.json"
THRESHOLD = 0.35   # lower = stricter

def extract_features(path):
    audio, sr = librosa.load(path, sr=16000)
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=20)
    return np.mean(mfcc.T, axis=0)

def load_database():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "r") as f:
        return json.load(f)

def verify_voice(live_path="Data/live_voice.wav"):
    try:
        live_feat = extract_features(live_path)
        db = load_database()

        for user, files in db.items():
            for f in files:
                ref_path = os.path.join(VOICE_DIR, f)
                ref_feat = extract_features(ref_path)

                score = cosine(live_feat, ref_feat)
                if score < THRESHOLD:
                    print(f"🔓 Voice matched: {user}")
                    return True

        return False

    except Exception as e:
        print("❌ Voice auth error:", e)
        return False

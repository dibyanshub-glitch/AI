import sounddevice as sd
import numpy as np
import queue
import time
import webrtcvad
from faster_whisper import WhisperModel

# =====================================================
# CONFIG
# =====================================================
SAMPLE_RATE = 16000
FRAME_DURATION_MS = 30                     # Required for WebRTC
BLOCK_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)  # 480 samples
END_SILENCE_SEC = 1.8
MIN_AUDIO_SEC = 0.6
MAX_AUDIO_SEC = 10

# Load Whisper model
model = WhisperModel("base", compute_type="int8")

# WebRTC VAD (0–3) | 3 = most aggressive
vad = webrtcvad.Vad(1)

audio_queue = queue.Queue()


# =====================================================
# AUDIO CALLBACK
# =====================================================
def audio_callback(indata, frames, time_info, status):
    if status:
        print(status)

    # Convert float32 → int16 for VAD
    audio_int16 = (indata.flatten() * 32768).astype(np.int16)
    audio_queue.put(audio_int16)


# =====================================================
# START STREAM
# =====================================================
def start_stream():
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        blocksize=BLOCK_SIZE,
        dtype="float32",
        callback=audio_callback,
    )
    stream.start()
    return stream


# =====================================================
# SPEECH RECOGNITION (PRODUCTION SAFE)
# =====================================================
def SpeechRecognitionStream():

    print("🎧 Streaming listening...")

    stream = start_stream()

    frames = []
    speech_started = False
    last_voice_time = time.time()

    try:
        while True:

            chunk = audio_queue.get()

            # WebRTC expects raw bytes
            pcm_bytes = chunk.tobytes()

            is_speech = vad.is_speech(pcm_bytes, SAMPLE_RATE)

            if is_speech:
                speech_started = True
                last_voice_time = time.time()
                frames.append(chunk)

            elif speech_started:
                frames.append(chunk)

            # Stop after silence
            # Stop only after REAL silence
            if speech_started:
                silence_duration = time.time() - last_voice_time

                # must have minimum speech first
                if silence_duration > END_SILENCE_SEC and len(frames) > SAMPLE_RATE * 0.8:
                    break

        stream.stop()
        stream.close()

        if not frames:
            return ""

        audio = np.concatenate(frames).astype(np.float32) / 32768.0

        # Reject too short speech
        if len(audio) < SAMPLE_RATE * MIN_AUDIO_SEC:
            return ""

        # Limit max duration
        max_samples = SAMPLE_RATE * MAX_AUDIO_SEC
        if len(audio) > max_samples:
            audio = audio[-max_samples:]

        # FINAL TRANSCRIPTION
        segments, _ = model.transcribe(
            audio,
            beam_size=5,
            best_of=5,
            temperature=0.0,
            vad_filter=True
        )

        final_text = " ".join([s.text for s in segments]).strip()

        # Garbage filter
        if not final_text or len(final_text) < 2:
            return ""

        print("🗣️ Final:", final_text)
        audio_queue.queue.clear()

        return final_text

    except Exception as e:
        print("Streaming STT error:", e)
        try:
            stream.stop()
            stream.close()
        except:
            pass
        return ""
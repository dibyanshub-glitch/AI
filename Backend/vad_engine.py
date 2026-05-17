import webrtcvad
import numpy as np

vad = webrtcvad.Vad(2)  # 0–3 (3 = aggressive)

SAMPLE_RATE = 16000

def has_speech(audio_chunk):
    """
    audio_chunk: float32 numpy array
    """
    if audio_chunk is None or len(audio_chunk) == 0:
        return False

    # convert float32 → int16
    pcm = (audio_chunk * 32768).astype(np.int16)

    # must be 10, 20, or 30 ms
    frame_length = int(SAMPLE_RATE * 0.02)  # 20ms

    if len(pcm) < frame_length:
        return False

    frame = pcm[:frame_length].tobytes()

    return vad.is_speech(frame, SAMPLE_RATE)
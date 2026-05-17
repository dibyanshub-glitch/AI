def _speak(text: str):
    text = _clean_text(text)
    if not text:
        return
    _offline_male_tts(text)

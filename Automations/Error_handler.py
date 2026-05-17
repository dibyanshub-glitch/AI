from Backend.TextToSpeech import TExtToSpeech
from Automations.Gui_feedback import gui_confirm

def handle_error(error: Exception, context=""):
    message = f"I faced an error {context}. Please check."
    print("ERROR:", error)
    gui_confirm(message)
    TExtToSpeech(message)

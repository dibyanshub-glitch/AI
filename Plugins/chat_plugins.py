from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TExtToSpeech
from Frontend.GUI import ShowTextToScreen

def can_handle(intent):
    return intent == "general_chat"

def handle(command, context):
    answer = ChatBot(command)
    ShowTextToScreen(f"Lukas : {answer}")
    TExtToSpeech(answer)

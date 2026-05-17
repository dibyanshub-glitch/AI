from Automations.Whatsapp import send_whatsapp_message
from Automations.NLP_parser import extract_whatsapp_details
from Automations.Gui_feedback import gui_confirm

def can_handle(intent):
    return intent == "send_whatsapp"

def handle(command, context):
    name, message = extract_whatsapp_details(command)
    send_whatsapp_message(name, message)
    gui_confirm(f"Message sent to {name}")

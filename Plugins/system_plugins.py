import os
from Automations.Gui_feedback import gui_confirm

def can_handle(intent):
    return intent == "system_control"

def handle(command, context):
    if "shutdown" in command:
        gui_confirm("Shutting down system")
        os.system("shutdown /s /t 1")

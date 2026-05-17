from Automations.Gpt_Code import generate_code
from Automations.Editor_writer import write_code_to_editor
from Automations.Gui_feedback import gui_confirm

def can_handle(intent):
    return intent == "write_code"

def handle(command, context):
    code = generate_code(command)
    path = write_code_to_editor(code)
    gui_confirm(f"Code written to {path}")

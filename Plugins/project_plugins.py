from Automations.Project_create import create_project
from Automations.Gui_feedback import gui_confirm

def can_handle(intent):
    return intent == "create_project"

def handle(command, context):
    project = "mywebsite"
    create_project(project)
    gui_confirm(f"Project {project} created")

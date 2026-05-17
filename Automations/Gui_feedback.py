from Frontend.GUI import ShowTextToScreen, SetAssistantStatus

def gui_confirm(message: str):
    SetAssistantStatus("Done")
    ShowTextToScreen(f"Lukas : {message}")

import subprocess
import shutil

def open_editor(preferred="auto"):

    if preferred == "vscode" or preferred == "auto":

        if shutil.which("code"):
            subprocess.Popen(["code"])
            return "vscode"

    if preferred == "notepad":
        subprocess.Popen(["notepad.exe"])
        return "notepad"

    # fallback
    subprocess.Popen(["notepad.exe"])
    return "notepad"

import subprocess
import pathlib
import os

from Backend.Automation import GenerateAndSaveCode


# -------------------------
# LANGUAGE EXTENSIONS
# -------------------------

EXT_MAP = {
    "python": ".py",
    "javascript": ".js",
    "cpp": ".cpp",
    "java": ".java",
    "html": ".html",
    "text": ".txt"
}


# -------------------------
# OPEN EDITORS
# -------------------------

def open_editor(editor, file_path):

    editor = editor.lower()

    try:

        if editor in ["vscode", "vs code", "code"]:
            subprocess.Popen(["code", str(file_path)])

        elif editor in ["pycharm"]:
            subprocess.Popen(["pycharm64.exe", str(file_path)])

        elif editor in ["notepad"]:
            subprocess.Popen(["notepad.exe", str(file_path)])

        elif editor in ["sublime"]:
            subprocess.Popen(["subl", str(file_path)])

        else:
            # fallback default system open
            os.startfile(file_path)

        return True

    except Exception as e:
        print("Editor open error:", e)
        return False


# -------------------------
# CREATE PROJECT
# -------------------------

def create_project(project_name):

    base = pathlib.Path("Projects") / project_name
    base.mkdir(parents=True, exist_ok=True)

    return base


# -------------------------
# UNIVERSAL CODE WRITER
# -------------------------

def smart_code_writer(prompt):

    prompt_lower = prompt.lower()

    # -----------------
    # DETECT EDITOR
    # -----------------

    editor = "vscode"

    if "notepad" in prompt_lower:
        editor = "notepad"

    elif "pycharm" in prompt_lower:
        editor = "pycharm"

    elif "sublime" in prompt_lower:
        editor = "sublime"

    elif "vscode" in prompt_lower or "vs code" in prompt_lower:
        editor = "vscode"

    # -----------------
    # GENERATE CODE
    # -----------------

    result = GenerateAndSaveCode(prompt)

    language = result["language"]
    code = result["code"]

    # -----------------
    # CREATE PROJECT
    # -----------------

    project_name = prompt.replace(" ", "_")[:25]
    project_folder = create_project(project_name)

    ext = EXT_MAP.get(language, ".txt")
    file_path = project_folder / f"main{ext}"

    file_path.write_text(code)

    # -----------------
    # OPEN EDITOR
    # -----------------

    open_editor(editor, file_path)

    return f"Code written in {editor}"

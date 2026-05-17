from Backend.Chatbot import ChatBot
from .editor_detector import open_editor
from .language_detector import detect_language
from .project_builder import create_project_structure
from .live_typing import type_code
from .context_memory import remember

import subprocess
import time


def smart_writer(prompt):

    lang, ext = detect_language(prompt)

    project_name = prompt.replace(" ", "_")[:30]

    root = create_project_structure(project_name, lang)

    file_path = f"{root}/main{ext}"

    # generate AI code
    code = ChatBot(prompt)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    # remember last language
    remember("last_language", lang)

    # open editor
    editor = open_editor("auto")

    time.sleep(2)

    # open file in VSCode if available
    if editor == "vscode":
        subprocess.Popen(["code", file_path])
    else:
        subprocess.Popen(["notepad.exe", file_path])

    time.sleep(2)

    # live typing effect
    type_code(code)

    return f"{lang} project created in {editor}"

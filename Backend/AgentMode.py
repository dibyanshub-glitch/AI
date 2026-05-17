import pyautogui
import subprocess
import os

def TakeScreenshot():
    img = pyautogui.screenshot()
    img.save("agent_screen.png")
    return "Screenshot saved."

def ExecuteShell(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        return result
    except Exception as e:
        return str(e)
    
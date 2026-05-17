import pyautogui
import time

def type_code(code):

    time.sleep(1)

    for char in code:
        pyautogui.write(char)
        time.sleep(0.002)

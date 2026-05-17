import subprocess
import time
import pyautogui
import pygetwindow as gw

def write_code_to_editor(text: str, language="txt"):
    """
    Guaranteed typing inside NEW Notepad only
    """

    try:
        # ✅ Open Notepad
        subprocess.Popen(["notepad.exe"])
        time.sleep(2)

        # ✅ Get ALL Notepad windows
        windows_before = gw.getWindowsWithTitle("Notepad")

        # open new notepad
        subprocess.Popen("start notepad", shell=True)
        time.sleep(2)

        windows_after = gw.getWindowsWithTitle("Notepad")

        # find NEW window
        new_windows = [w for w in windows_after if w not in windows_before]

        if new_windows:
            notepad = new_windows[0]
        else:
            notepad = windows_after[-1]

        # ✅ Activate window
        notepad.activate()
        time.sleep(0.7)

        # ✅ Click inside safely (center of window)
        x = notepad.left + (notepad.width // 2)
        y = notepad.top + (notepad.height // 2)
        pyautogui.click(x, y)
        time.sleep(0.3)

        # ✅ Clear content
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")

        # ✅ TYPE LINE BY LINE (slightly slower = stable)
        for line in text.split("\n"):
            pyautogui.write(line, interval=0.015)
            pyautogui.press("enter")
            time.sleep(0.02)

    except Exception as e:
        print("Typing error:", e)
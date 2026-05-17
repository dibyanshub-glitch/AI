import winreg
import os
import json

REG_PATHS = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
]

def scan_installed_apps():
    apps = {}

    for hive, path in REG_PATHS:
        try:
            reg_key = winreg.OpenKey(hive, path)
        except:
            continue

        for i in range(0, winreg.QueryInfoKey(reg_key)[0]):
            try:
                subkey_name = winreg.EnumKey(reg_key, i)
                subkey = winreg.OpenKey(reg_key, subkey_name)

                try:
                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                except:
                    continue

                try:
                    install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                except:
                    install_location = ""

                try:
                    exe = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                except:
                    exe = ""

                if name:
                    apps[name.lower()] = {
                        "name": name,
                        "path": install_location,
                        "exe": exe
                    }

            except:
                continue

    return apps

import subprocess

def launch_app(app_name):
    apps = scan_installed_apps()

    app_name = app_name.lower()

    for name, info in apps.items():
        if app_name in name:

            exe = info["exe"]

            if exe and os.path.exists(exe.split(",")[0]):
                subprocess.Popen(exe.split(",")[0])
                return f"{info['name']} opened"

            path = info["path"]
            if path and os.path.exists(path):
                subprocess.Popen(path)
                return f"{info['name']} opened"

    return None


def cache_apps():
    apps = scan_installed_apps()
    with open("Data/app_cache.json","w") as f:
        json.dump(apps,f)

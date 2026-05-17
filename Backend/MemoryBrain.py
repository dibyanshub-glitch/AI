import json
import os

MEMORY_FILE = "Data/Memory.json"

def _load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_memory(mem):
    os.makedirs("Data", exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2)


# ---------- STORE ----------
def remember(key, value):
    mem = _load_memory()
    mem[key] = value
    _save_memory(mem)
    return f"I will remember that {key} is {value}"


# ---------- GET ----------
def recall(key):
    mem = _load_memory()
    return mem.get(key)


# ---------- DELETE ----------
def forget(key):
    mem = _load_memory()
    if key in mem:
        del mem[key]
        _save_memory(mem)
        return f"I forgot {key}"
    return "I don't remember that"

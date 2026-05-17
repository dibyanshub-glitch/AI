import json
from pathlib import Path

MEMORY_FILE = Path("Data/writer_memory.json")

def remember(key, value):

    data = {}
    if MEMORY_FILE.exists():
        data = json.loads(MEMORY_FILE.read_text())

    data[key] = value
    MEMORY_FILE.write_text(json.dumps(data, indent=2))


def recall(key):

    if not MEMORY_FILE.exists():
        return None

    data = json.loads(MEMORY_FILE.read_text())
    return data.get(key)

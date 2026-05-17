import json
from pathlib import Path

MEMORY = Path("Data/dev_memory.json")


def remember_project(plan):

    data = []

    if MEMORY.exists():
        data = json.loads(MEMORY.read_text())

    data.append(plan)

    MEMORY.write_text(json.dumps(data, indent=2))

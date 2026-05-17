import json
from pathlib import Path

LEARN_FILE = Path("Data/autonomous_learning.json")


def learn_from_result(task, result):

    data = []

    if LEARN_FILE.exists():
        data = json.loads(LEARN_FILE.read_text())

    data.append({
        "task": task,
        "result": result
    })

    LEARN_FILE.write_text(json.dumps(data, indent=2))

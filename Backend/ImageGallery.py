import json
from pathlib import Path

GALLERY_FILE = Path("Data/gallery.json")

if not GALLERY_FILE.exists():
    GALLERY_FILE.write_text("[]")


def save_to_gallery(filepath):

    data = json.loads(GALLERY_FILE.read_text())
    data.append(str(filepath))
    GALLERY_FILE.write_text(json.dumps(data, indent=2))

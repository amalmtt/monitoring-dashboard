import json

from constants import DATA_FILE


def load_rooms():
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_rooms(rooms):
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(rooms, f, indent=2, ensure_ascii=False)
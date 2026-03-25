from pathlib import Path

PAGE_TITLE = "UV Monitoring Dashboard"
DATA_FILE = Path("data.json")
DEFAULT_LIFETIME_HOURS = 6 * 30 * 24  # 4320h

ROOM_TYPE_MAP = {
    "All": "All",
    "Broodstock": "broodstock",
    "Larval": "larval",
    "Nursery1": "nursery1",
    "Nursery2": "nursery2",
}

ROOM_TYPE_SUMMARY = [
    ("Broodstock", "broodstock"),
    ("Larval", "larval"),
    ("Nursery1", "nursery1"),
    ("Nursery2", "nursery2"),
]
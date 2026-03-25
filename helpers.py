import csv
import io
import math
from datetime import datetime

from constants import DEFAULT_LIFETIME_HOURS


def parse_datetime(value):
    if not value:
        return None

    text = str(value).strip().replace("T", " ")

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass

    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def now_string():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def short_date(value):
    dt = parse_datetime(value)
    if not dt:
        return "N/A"
    return dt.strftime("%Y-%m-%d")


def normalize_status(value):
    status = str(value or "").strip().title()
    if status not in ["OK", "Warning", "Critical"]:
        return "OK"
    return status


def normalize_manual_status(value):
    raw = str(value or "").strip()
    if raw == "":
        return ""
    return normalize_status(raw)


def format_hours(hours):
    if hours is None:
        return "N/A"
    if hours >= 0:
        return f"{hours}h"
    return f"Overdue {abs(hours)}h"


def get_lifetime_hours(item):
    raw = item.get("lifetime_hours", DEFAULT_LIFETIME_HOURS)
    try:
        value = float(raw)
        return value if value > 0 else DEFAULT_LIFETIME_HOURS
    except (TypeError, ValueError):
        return DEFAULT_LIFETIME_HOURS


def calculate_used_hours(start_date):
    start_dt = parse_datetime(start_date)
    if start_dt is None:
        return 0

    elapsed_hours = (datetime.now() - start_dt).total_seconds() / 3600
    return max(0, math.ceil(elapsed_hours))


def calculate_remaining_hours(start_date, lifetime_hours):
    return math.ceil(lifetime_hours - calculate_used_hours(start_date))


def status_badge(status):
    normalized = str(status).strip().lower()

    if normalized == "ok":
        return '<span class="badge badge-ok">OK</span>'
    if normalized == "warning":
        return '<span class="badge badge-warning">Warning</span>'
    if normalized == "critical":
        return '<span class="badge badge-critical">Critical</span>'

    return f'<span class="badge badge-neutral">{status}</span>'


def overdue_badge(remaining_hours):
    if remaining_hours < 0:
        return f'<span class="pill pill-overdue">OVERDUE {abs(remaining_hours)}h</span>'
    return ""


def room_colors(room_state):
    base_background = "linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)"
    neutral_border = "#d8e0ea"

    if room_state == "OK":
        return {
            "background": base_background,
            "border": neutral_border,
            "title": "#0f172a",
            "badge": '<span class="badge badge-ok">OK</span>',
            "accent": "#16a34a",
        }

    if room_state == "Warning":
        return {
            "background": base_background,
            "border": neutral_border,
            "title": "#0f172a",
            "badge": '<span class="badge badge-warning">Warning</span>',
            "accent": "#d97706",
        }

    return {
        "background": base_background,
        "border": neutral_border,
        "title": "#0f172a",
        "badge": '<span class="badge badge-critical">Critical</span>',
        "accent": "#dc2626",
    }


def iter_room_items(room):
    room_technician = room.get("technician", "N/A")

    for equipment in room.get("equipment", []):
        equipment_name = equipment.get("equipment_name", "")
        equipment_type = equipment.get("type", "")
        equipment_id = equipment.get("equipment_id", "")

        if equipment.get("components"):
            for component in equipment.get("components", []):
                yield {
                    "item_id": component.get("component_id", ""),
                    "label": f"{equipment_name} / {component.get('component_name', '')}",
                    "short_name": component.get("component_name", ""),
                    "group_name": equipment_name,
                    "room_type": room.get("room_type", ""),
                    "kind": "component",
                    "status": normalize_status(component.get("status", "OK")),
                    "start_date": component.get("start_date", ""),
                    "lifetime_hours": get_lifetime_hours(component),
                    "technician": component.get("technician", room_technician),
                    "last_updated": component.get("last_updated", room.get("last_updated", "")),
                    "notes": component.get("notes", ""),
                    "equipment_id": equipment_id,
                    "component_id": component.get("component_id", ""),
                    "equipment_type": equipment_type,
                }
        else:
            yield {
                "item_id": equipment_id,
                "label": equipment_name,
                "short_name": equipment_name,
                "group_name": equipment_name,
                "room_type": room.get("room_type", ""),
                "kind": "equipment",
                "status": normalize_status(equipment.get("status", "OK")),
                "start_date": equipment.get("start_date", ""),
                "lifetime_hours": get_lifetime_hours(equipment),
                "technician": equipment.get("technician", room_technician),
                "last_updated": equipment.get("last_updated", room.get("last_updated", "")),
                "notes": equipment.get("notes", ""),
                "equipment_id": equipment_id,
                "component_id": None,
                "equipment_type": equipment_type,
            }


def get_room_auto_status(room):
    states = [item["status"] for item in iter_room_items(room)]

    if not states:
        return "OK"
    if "Critical" in states:
        return "Critical"
    if "Warning" in states:
        return "Warning"
    return "OK"


def get_room_state(room):
    manual = normalize_manual_status(room.get("manual_status", ""))
    if manual:
        return manual
    return get_room_auto_status(room)


def get_room_start_date(room):
    dates = []
    for item in iter_room_items(room):
        dt = parse_datetime(item["start_date"])
        if dt:
            dates.append(dt)

    if not dates:
        return "N/A"
    return min(dates).strftime("%Y-%m-%d %H:%M")


def get_room_used_hours(room):
    values = [calculate_used_hours(item["start_date"]) for item in iter_room_items(room)]
    if not values:
        return 0
    return max(values)


def get_room_remaining_hours(room):
    values = [
        calculate_remaining_hours(item["start_date"], item["lifetime_hours"])
        for item in iter_room_items(room)
    ]
    if not values:
        return DEFAULT_LIFETIME_HOURS
    return min(values)


def get_room_last_updated(room):
    dates = []

    room_dt = parse_datetime(room.get("last_updated"))
    if room_dt:
        dates.append(room_dt)

    for item in iter_room_items(room):
        dt = parse_datetime(item.get("last_updated"))
        if dt:
            dates.append(dt)

    if not dates:
        return "N/A"

    return max(dates).strftime("%Y-%m-%d %H:%M")


def get_room_item_count(room):
    return len(list(iter_room_items(room)))


def get_room_status_counts(room):
    ok_count = 0
    warning_count = 0
    critical_count = 0

    for item in iter_room_items(room):
        if item["status"] == "OK":
            ok_count += 1
        elif item["status"] == "Warning":
            warning_count += 1
        elif item["status"] == "Critical":
            critical_count += 1

    return ok_count, warning_count, critical_count


def get_room_overdue_count(room):
    count = 0
    for item in iter_room_items(room):
        remaining = calculate_remaining_hours(item["start_date"], item["lifetime_hours"])
        if remaining < 0:
            count += 1
    return count


def category_summary(rooms, room_type):
    subset = [room for room in rooms if room.get("room_type", "") == room_type]
    total = len(subset)
    critical = sum(1 for room in subset if get_room_state(room) == "Critical")
    warning = sum(1 for room in subset if get_room_state(room) == "Warning")
    overdue = sum(get_room_overdue_count(room) for room in subset)
    return total, critical, warning, overdue


def room_sort_key(room, mode):
    state_priority = {"Critical": 0, "Warning": 1, "OK": 2}
    state = get_room_state(room)
    remaining = get_room_remaining_hours(room)
    name = str(room.get("room_name", ""))

    if mode == "Urgency":
        return (state_priority[state], remaining, name)
    if mode == "Remaining time":
        return (remaining, state_priority[state], name)
    if mode == "Last updated":
        dt = parse_datetime(get_room_last_updated(room))
        return (dt is None, -(dt.timestamp()) if dt else 0)
    if mode == "Room name":
        return (name.lower(),)
    return (state_priority[state], remaining, name)


def find_room_by_id(rooms, room_id):
    for room in rooms:
        if str(room.get("room_id")) == str(room_id):
            return room
    return None


def find_room_index_by_id(rooms, room_id):
    for idx, room in enumerate(rooms):
        if str(room.get("room_id")) == str(room_id):
            return idx
    return None


def update_item_in_rooms(rooms, room_id, item_id, new_data):
    for room in rooms:
        if str(room.get("room_id")) != str(room_id):
            continue

        for equipment in room.get("equipment", []):
            if equipment.get("components"):
                for component in equipment.get("components", []):
                    if str(component.get("component_id")) == str(item_id):
                        component.update(new_data)
                        return True
            else:
                if str(equipment.get("equipment_id")) == str(item_id):
                    equipment.update(new_data)
                    return True

    return False


def export_rows(rooms):
    rows = []
    for room in rooms:
        auto_status = get_room_auto_status(room)
        displayed_status = get_room_state(room)
        manual_status = normalize_manual_status(room.get("manual_status", ""))

        for item in iter_room_items(room):
            used = calculate_used_hours(item["start_date"])
            remaining = calculate_remaining_hours(item["start_date"], item["lifetime_hours"])
            rows.append(
                {
                    "room_id": room.get("room_id", ""),
                    "room_name": room.get("room_name", ""),
                    "room_type": room.get("room_type", ""),
                    "room_technician": room.get("technician", ""),
                    "room_manual_status": manual_status or "Auto",
                    "room_auto_status": auto_status,
                    "room_displayed_status": displayed_status,
                    "item_group": item["group_name"],
                    "item_name": item["short_name"],
                    "item_kind": item["kind"],
                    "item_status": item["status"],
                    "start_date": item["start_date"],
                    "used_hours": used,
                    "remaining_hours": remaining,
                    "lifetime_hours": item["lifetime_hours"],
                    "item_technician": item["technician"],
                    "last_updated": item["last_updated"],
                    "notes": item["notes"],
                }
            )
    return rows


def export_csv_bytes(rooms):
    rows = export_rows(rooms)
    output = io.StringIO()

    fieldnames = [
        "room_id",
        "room_name",
        "room_type",
        "room_technician",
        "room_manual_status",
        "room_auto_status",
        "room_displayed_status",
        "item_group",
        "item_name",
        "item_kind",
        "item_status",
        "start_date",
        "used_hours",
        "remaining_hours",
        "lifetime_hours",
        "item_technician",
        "last_updated",
        "notes",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")
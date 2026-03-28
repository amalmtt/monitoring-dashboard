import json
import math
import re
from datetime import date, datetime, time, timedelta

from constants import COMPONENT_LIFETIME_HOURS, DATA_FILE, INITIAL_LIFETIME_LABEL


def _parse_date(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    text = str(value).strip()

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass

    return None


def _serialize_date(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value.date().isoformat()

    if isinstance(value, date):
        return value.isoformat()

    return str(value)


def _parse_replacement_date(text):
    raw = str(text or "").strip()
    if raw == "":
        return None

    match = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})", raw)
    if not match:
        return None

    value = match.group(1)

    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%d/%m/%y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass

    return None


def _parse_replaced_lamp_numbers(text):
    raw = str(text or "").strip()
    if raw == "":
        return set()

    matches = re.findall(r"lamp\s*#?\s*(\d+)", raw, flags=re.IGNORECASE)
    return {int(value) for value in matches}


def _compute_component_dates(start_date):
    if not start_date:
        return None, None, None

    start_dt = datetime.combine(start_date, time.min)
    end_dt = start_dt + timedelta(hours=COMPONENT_LIFETIME_HOURS)
    remaining_hours = math.ceil((end_dt - datetime.now()).total_seconds() / 3600)
    remaining_days = math.floor(max(remaining_hours, 0) / 24)

    return end_dt.date(), remaining_days, remaining_hours


def _component_status(component):
    remaining_hours = component.get("remaining_hours")

    if remaining_hours is None:
        return "Warning"

    try:
        remaining_hours = float(remaining_hours)
    except (TypeError, ValueError):
        return "Warning"

    if remaining_hours < 0:
        return "Out of service"

    if remaining_hours <= 90 * 24:
        return "Warning"

    return "Normal"


def _build_components(system):
    components = []

    base_start = system.get("start_date")
    lamp_replacement_text = str(system.get("lamp_replacement") or "").strip()
    ballast_replacement_text = str(system.get("ballast_replacement") or "").strip()

    replaced_lamps = _parse_replaced_lamp_numbers(lamp_replacement_text)
    replaced_lamp_date = _parse_replacement_date(lamp_replacement_text)
    ballast_replacement_date = _parse_replacement_date(ballast_replacement_text)

    ballast_start = ballast_replacement_date or base_start
    ballast_end, ballast_remaining_days, ballast_remaining_hours = _compute_component_dates(ballast_start)

    components.append(
        {
            "component_id": f'{system.get("system_id")}_ballast',
            "component_name": "Ballast",
            "component_type": "ballast",
            "start_date": ballast_start,
            "end_date": ballast_end,
            "remaining_days": ballast_remaining_days,
            "remaining_hours": ballast_remaining_hours,
            "replacement_note": ballast_replacement_text,
            "lifetime_label": INITIAL_LIFETIME_LABEL,
            "status": _component_status({"remaining_hours": ballast_remaining_hours}),
        }
    )

    lamp_count = int(float(system.get("number_of_lamps") or 0))

    for lamp_number in range(1, lamp_count + 1):
        lamp_start = base_start
        replacement_note = ""

        if lamp_number in replaced_lamps and replaced_lamp_date:
            lamp_start = replaced_lamp_date
            replacement_note = lamp_replacement_text

        lamp_end, lamp_remaining_days, lamp_remaining_hours = _compute_component_dates(lamp_start)

        components.append(
            {
                "component_id": f'{system.get("system_id")}_lamp_{lamp_number}',
                "component_name": f"Lamp {lamp_number}",
                "component_type": "lamp",
                "start_date": lamp_start,
                "end_date": lamp_end,
                "remaining_days": lamp_remaining_days,
                "remaining_hours": lamp_remaining_hours,
                "replacement_note": replacement_note,
                "lifetime_label": INITIAL_LIFETIME_LABEL,
                "status": _component_status({"remaining_hours": lamp_remaining_hours}),
            }
        )

    return components


def _apply_system_lifetime_from_components(system):
    components = system.get("components", [])
    valid_components = [c for c in components if c.get("start_date") and c.get("end_date")]

    if not valid_components:
        return system

    system["start_date"] = min(c["start_date"] for c in valid_components)
    system["end_date"] = min(c["end_date"] for c in valid_components)
    system["remaining_days"] = min(c["remaining_days"] for c in valid_components if c.get("remaining_days") is not None)
    system["remaining_hours"] = min(c["remaining_hours"] for c in valid_components if c.get("remaining_hours") is not None)

    return system


def load_monitoring_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"{DATA_FILE} not found. Put the converted data.json in the project root."
        )

    with DATA_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    systems = data.get("systems", [])

    for system in systems:
        system["start_date"] = _parse_date(system.get("start_date"))
        system["end_date"] = _parse_date(system.get("end_date"))
        system["components"] = _build_components(system)
        _apply_system_lifetime_from_components(system)

    return data


def save_monitoring_data(data):
    serializable = {
        "meta": data.get("meta", {}),
        "systems": [],
    }

    for system in data.get("systems", []):
        system_copy = dict(system)
        system_copy.pop("components", None)
        system_copy["start_date"] = _serialize_date(system_copy.get("start_date"))
        system_copy["end_date"] = _serialize_date(system_copy.get("end_date"))
        serializable["systems"].append(system_copy)

    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)
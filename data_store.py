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


def _to_int_count(value, default=0):
    try:
        return int(float(value or default))
    except (TypeError, ValueError):
        return default


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


def _component_status_from_hours(remaining_hours):
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


def _normalize_component_replacements(system):
    replacements = {}

    raw_replacements = system.get("component_replacements", {}) or {}
    for key, value in raw_replacements.items():
        parsed = _parse_date(value)
        if parsed:
            replacements[key] = parsed

    lamp_replacement_text = str(system.get("lamp_replacement") or "").strip()
    ballast_replacement_text = str(system.get("ballast_replacement") or "").strip()

    legacy_lamp_date = _parse_replacement_date(lamp_replacement_text)
    legacy_lamps = _parse_replaced_lamp_numbers(lamp_replacement_text)
    for lamp_number in legacy_lamps:
        if legacy_lamp_date:
            replacements.setdefault(f"Lamp {lamp_number}", legacy_lamp_date)

    legacy_ballast_date = _parse_replacement_date(ballast_replacement_text)
    if legacy_ballast_date and "Ballast" not in replacements and "Ballast 1" not in replacements:
        replacements["Ballast 1"] = legacy_ballast_date

    return replacements


def _normalize_component_remarks(system):
    raw = system.get("component_remarks", {}) or {}
    remarks = {}

    for key, value in raw.items():
        text = str(value or "").strip()
        if text and text.lower() not in {"n/a", "na", "-", "?"}:
            remarks[key] = text

    legacy_ballast = remarks.pop("Ballast", None)
    if legacy_ballast and "Ballast 1" not in remarks:
        remarks["Ballast 1"] = legacy_ballast

    return remarks


def _build_components(system):
    components = []

    base_start = system.get("start_date")
    lamp_replacement_text = str(system.get("lamp_replacement") or "").strip()
    ballast_replacement_text = str(system.get("ballast_replacement") or "").strip()

    component_replacements = _normalize_component_replacements(system)
    component_remarks = _normalize_component_remarks(system)

    system["component_replacements"] = component_replacements
    system["component_remarks"] = component_remarks

    lamp_count = _to_int_count(system.get("number_of_lamps"), 0)
    ballast_count = _to_int_count(system.get("number_of_ballasts"), lamp_count)

    system["number_of_lamps"] = lamp_count
    system["number_of_ballasts"] = ballast_count

    replaced_lamps = _parse_replaced_lamp_numbers(lamp_replacement_text)
    replaced_lamp_date = _parse_replacement_date(lamp_replacement_text)
    ballast_replacement_date = _parse_replacement_date(ballast_replacement_text)

    for ballast_number in range(1, ballast_count + 1):
        ballast_key = f"Ballast {ballast_number}"

        ballast_start = base_start
        replacement_note = ""

        if component_replacements.get(ballast_key):
            ballast_start = component_replacements[ballast_key]
            replacement_note = f'{ballast_key} replaced ({component_replacements[ballast_key].strftime("%m/%d/%y")})'
        elif ballast_number == 1 and ballast_replacement_date:
            ballast_start = ballast_replacement_date
            replacement_note = ballast_replacement_text

        ballast_end, ballast_remaining_days, ballast_remaining_hours = _compute_component_dates(ballast_start)

        components.append(
            {
                "component_id": f'{system.get("system_id")}_ballast_{ballast_number}',
                "component_name": ballast_key,
                "component_type": "ballast",
                "start_date": ballast_start,
                "end_date": ballast_end,
                "remaining_days": ballast_remaining_days,
                "remaining_hours": ballast_remaining_hours,
                "replacement_note": replacement_note,
                "remark": component_remarks.get(ballast_key, ""),
                "lifetime_label": INITIAL_LIFETIME_LABEL,
                "status": _component_status_from_hours(ballast_remaining_hours),
            }
        )

    for lamp_number in range(1, lamp_count + 1):
        lamp_key = f"Lamp {lamp_number}"

        lamp_start = base_start
        replacement_note = ""

        if component_replacements.get(lamp_key):
            lamp_start = component_replacements[lamp_key]
            replacement_note = f'{lamp_key} replaced ({component_replacements[lamp_key].strftime("%m/%d/%y")})'
        elif lamp_number in replaced_lamps and replaced_lamp_date:
            lamp_start = replaced_lamp_date
            replacement_note = lamp_replacement_text

        lamp_end, lamp_remaining_days, lamp_remaining_hours = _compute_component_dates(lamp_start)

        components.append(
            {
                "component_id": f'{system.get("system_id")}_lamp_{lamp_number}',
                "component_name": lamp_key,
                "component_type": "lamp",
                "start_date": lamp_start,
                "end_date": lamp_end,
                "remaining_days": lamp_remaining_days,
                "remaining_hours": lamp_remaining_hours,
                "replacement_note": replacement_note,
                "remark": component_remarks.get(lamp_key, ""),
                "lifetime_label": INITIAL_LIFETIME_LABEL,
                "status": _component_status_from_hours(lamp_remaining_hours),
            }
        )

    return components


def _apply_system_lifetime_from_components(system):
    components = system.get("components", [])
    valid_components = [c for c in components if c.get("start_date") and c.get("end_date")]

    if not valid_components:
        return system

    remaining_days_values = [c.get("remaining_days") for c in valid_components if c.get("remaining_days") is not None]
    remaining_hours_values = [c.get("remaining_hours") for c in valid_components if c.get("remaining_hours") is not None]

    system["start_date"] = min(c["start_date"] for c in valid_components)
    system["end_date"] = min(c["end_date"] for c in valid_components)
    system["remaining_days"] = min(remaining_days_values) if remaining_days_values else None
    system["remaining_hours"] = min(remaining_hours_values) if remaining_hours_values else None

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
        system["component_replacements"] = _normalize_component_replacements(system)
        system["component_remarks"] = _normalize_component_remarks(system)
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

        component_replacements = system_copy.get("component_replacements", {}) or {}
        serializable_replacements = {}
        for key, value in component_replacements.items():
            serializable_replacements[key] = _serialize_date(value)
        system_copy["component_replacements"] = serializable_replacements

        component_remarks = system_copy.get("component_remarks", {}) or {}
        serializable_remarks = {}
        for key, value in component_remarks.items():
            text = str(value or "").strip()
            if text:
                serializable_remarks[key] = text
        system_copy["component_remarks"] = serializable_remarks

        system_copy["start_date"] = _serialize_date(system_copy.get("start_date"))
        system_copy["end_date"] = _serialize_date(system_copy.get("end_date"))
        serializable["systems"].append(system_copy)

    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)
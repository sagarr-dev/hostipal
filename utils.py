# utils.py
# Validators and helpers for Hospital Management System

from datetime import datetime, time as dt_time
from typing import Tuple, Optional


def validate_time_str(t: str) -> Tuple[bool, Optional[str]]:
    """
    Validate time string in HH:MM format (24-hour).
    Returns (is_valid, error_message)
    """
    try:
        datetime.strptime(t, "%H:%M")
        return True, None
    except Exception:
        return False, "Time must be in HH:MM 24-hour format (e.g., 09:30)."


def validate_date_str(d: str) -> Tuple[bool, Optional[str]]:
    """
    Validate date string in YYYY-MM-DD format.
    """
    try:
        datetime.strptime(d, "%Y-%m-%d")
        return True, None
    except Exception:
        return False, "Date must be in YYYY-MM-DD format (e.g., 2025-11-26)."


def parse_time(t: str) -> dt_time:
    return datetime.strptime(t, "%H:%M").time()


def time_in_working_hours(working_hours: Optional[str], appointment_time: str) -> Tuple[bool, Optional[str]]:
    """
    working_hours is expected in 'HH:MM-HH:MM' format, e.g. '09:00-17:00'.
    Returns (True, None) if appointment_time within working hours.
    """
    if not working_hours:
        # No working hours set -> treat as allowed (or you could block)
        return True, None

    try:
        parts = working_hours.split("-")
        if len(parts) != 2:
            return False, "Doctor working hours must be in 'HH:MM-HH:MM' format."

        start = parse_time(parts[0].strip())
        end = parse_time(parts[1].strip())
        appt_t = parse_time(appointment_time)

        # check appointment is >= start and < end
        if start <= appt_t < end:
            return True, None
        else:
            return False, f"Appointment time {appointment_time} is outside doctor's working hours ({working_hours})."
    except Exception:
        return False, "Invalid working hours or appointment time format."


def short_display(row) -> str:
    """Small helper to show row in summary displays."""
    if not row:
        return ""
    # sqlite3.Row supports dict-like access
    parts = []
    if "id" in row.keys():
        parts.append(f"#{row['id']}")
    if "name" in row.keys():
        parts.append(row["name"])
    if "date" in row.keys() and "time" in row.keys():
        parts.append(f"{row['date']} {row['time']}")
    return " | ".join(parts)

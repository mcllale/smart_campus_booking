"""
models/booking.py
Booking data class plus the overlap-checking logic used whenever a new
booking is created. Kept separate from Lecturer so the rule is defined
once and reused everywhere a booking might be inserted, instead of being
duplicated across the codebase.
"""
from database import get_connection


class Booking:
    def __init__(self, booking_id, resource_id, user_id, campus, date,
                 start_time, duration_min, status="active"):
        self.booking_id = booking_id
        self.resource_id = resource_id
        self.user_id = user_id
        self.campus = campus
        self.date = date
        self.start_time = start_time
        self.duration_min = duration_min
        self.status = status

    def start_minutes(self):
        return _to_minutes(self.start_time)

    def end_minutes(self):
        return self.start_minutes() + self.duration_min


def _to_minutes(hhmm):
    hours, minutes = map(int, hhmm.split(":"))
    return hours * 60 + minutes


def overlaps_existing(resource_id, date_str, start_time, duration_min, exclude_booking_id=None):
    """Return True if [start_time, start_time + duration_min) overlaps any
    active booking already stored for this resource on this date.
    `exclude_booking_id` lets a booking be checked against everything
    except itself (useful if the system is later extended to support
    editing an existing booking)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT booking_id, start_time, duration_min FROM bookings
        WHERE resource_id = ? AND date = ? AND status = 'active'
    """, (resource_id, date_str))
    rows = cur.fetchall()
    conn.close()

    new_start = _to_minutes(start_time)
    new_end = new_start + duration_min
    for booking_id, existing_start, existing_duration in rows:
        if exclude_booking_id is not None and booking_id == exclude_booking_id:
            continue
        ex_start = _to_minutes(existing_start)
        ex_end = ex_start + existing_duration
        if new_start < ex_end and ex_start < new_end:
            return True
    return False

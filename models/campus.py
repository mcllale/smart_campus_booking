"""
models/campus.py
Campus class encapsulating each campus's booking policy. Booking rules are
kept separate from core booking logic: Lecturer.book_resource() just calls
campus.validate_booking(). Adding a new campus with new rules only requires
inserting a row into the `campuses` table - no other code needs to change.
"""
from datetime import datetime, date

from database import get_connection


class Campus:
    def __init__(self, name, max_duration, open_hour, close_hour,
                 max_bookings_per_day, policy_description):
        self.name = name
        self.max_duration = max_duration
        self.open_hour = open_hour
        self.close_hour = close_hour
        self.max_bookings_per_day = max_bookings_per_day
        self.policy_description = policy_description

    def validate_booking(self, date_str, start_time, duration_min, user_id):
        """Raise ValueError with a clear, user-facing message if the
        requested booking breaks this campus's policy. Returns silently
        if the booking is allowed."""
        try:
            booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")
        if booking_date < date.today():
            raise ValueError("Date cannot be in the past.")

        try:
            start_hour, start_min = map(int, start_time.split(":"))
        except ValueError:
            raise ValueError("Start time must be in HH:MM format.")

        if duration_min <= 0 or duration_min > self.max_duration:
            raise ValueError(
                f"Duration must be between 1 and {self.max_duration} minutes at {self.name}."
            )

        end_total_minutes = start_hour * 60 + start_min + duration_min
        if start_hour < self.open_hour or end_total_minutes > self.close_hour * 60:
            raise ValueError(
                f"{self.name} only allows bookings between "
                f"{self.open_hour:02d}:00 and {self.close_hour:02d}:00."
            )

        if self.max_bookings_per_day is not None:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*) FROM bookings
                WHERE user_id = ? AND campus = ? AND date = ? AND status = 'active'
            """, (user_id, self.name, date_str))
            count = cur.fetchone()[0]
            conn.close()
            if count >= self.max_bookings_per_day:
                raise ValueError(
                    f"{self.name} limits lecturers to {self.max_bookings_per_day} "
                    f"booking(s) per day, and you have reached that limit."
                )


def get_campus(name):
    """Load a single Campus by name, or raise ValueError if unknown."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT campus_name, max_duration, open_hour, close_hour,
               max_bookings_per_day, policy_description
        FROM campuses WHERE campus_name = ?
    """, (name,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        raise ValueError(f"Unknown campus: {name}")
    return Campus(*row)


def list_campus_names():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT campus_name FROM campuses ORDER BY campus_name")
    names = [r[0] for r in cur.fetchall()]
    conn.close()
    return names


def get_all_campuses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT campus_name, max_duration, open_hour, close_hour,
               max_bookings_per_day, policy_description
        FROM campuses ORDER BY campus_name
    """)
    rows = cur.fetchall()
    conn.close()
    return [Campus(*row) for row in rows]

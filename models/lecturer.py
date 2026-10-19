'''
models/lecturer.py
Lecturer role: browses resources at the selected campus, creates bookings
(subject to that campus's policy and the overlap rule), and manages their
own booking history.
'''
from datetime import date

from database import get_connection
from models.user import User
from models.campus import get_campus
from models.booking import overlaps_existing


class Lecturer(User):
    '''
    The Lecturer role can view available resources,
    make bookings, and manage their own bookings.
    '''
    def __init__(self, user_id, username, password_hash, role="lecturer"):
        super().__init__(user_id, username, password_hash, role)

    def view_available_resources(self, campus_name):
        '''Return [(resource_id, name, resource_type), ...] for a campus.'''
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT resource_id, name, resource_type
            FROM resources
            WHERE campus = ? ORDER BY resource_id
        ''', (campus_name,))
        rows = cur.fetchall()
        conn.close()
        return rows

    def book_resource(self, campus_name, resource_id, date_str, start_time, duration_min):
        '''
        Validate against the campus's policy and the overlap rule, then
        insert the booking. Raises ValueError with a user-facing message
        on any failure; does nothing to the database in that case.
        '''
        campus = get_campus(campus_name)
        campus.validate_booking(date_str, start_time, duration_min, self.user_id)

        if overlaps_existing(resource_id, date_str, start_time, duration_min):
            raise ValueError("That resource is already booked for an overlapping time slot.")

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO bookings (resource_id, user_id, campus, date, start_time, duration_min, status)
                VALUES (?, ?, ?, ?, ?, ?, 'active')
            ''', (resource_id, self.user_id, campus_name, date_str, start_time, duration_min))
            conn.commit()
        finally:
            conn.close()

    def view_my_bookings(self, include_past=True):
        '''Return [(booking_id, resource_id, campus, date, start_time,
        duration_min, status), ...] for this lecturer.'''
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT booking_id, resource_id, campus, date, start_time, duration_min, status
            FROM bookings
            WHERE user_id = ?
            ORDER BY date, start_time
        ''', (self.user_id,))
        rows = cur.fetchall()
        conn.close()

        if include_past:
            return rows
        today_str = date.today().isoformat()
        return [r for r in rows if r[3] >= today_str and r[6] == 'active']

    def cancel_booking(self, booking_id):
        '''Cancel one of this lecturer's own, still-upcoming bookings.'''
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, date, status FROM bookingsWHERE booking_id = ?", (booking_id,))
        row = cur.fetchone()
        if row is None:
            conn.close()
            raise ValueError("Booking not found.")

        owner_id, booking_date, status = row
        if owner_id != self.user_id:
            conn.close()
            raise ValueError("You can only cancel your own bookings.")
        if status == 'cancelled':
            conn.close()
            raise ValueError("This booking is already cancelled.")
        if booking_date < date.today().isoformat():
            conn.close()
            raise ValueError("Past bookings cannot be cancelled.")

        cur.execute("UPDATE bookings SET status = 'cancelled' WHERE booking_id = ?", (booking_id,))
        conn.commit()
        conn.close()

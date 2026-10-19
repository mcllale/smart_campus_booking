"""
models/campus_administrator.py
Campus Administrator role: manages resources at a chosen campus and
monitors bookings/usage trends there.
"""
from collections import Counter

from database import get_connection
from models.user import User


class CampusAdministrator(User):
    def __init__(self, user_id, username, password_hash, role="admin"):
        super().__init__(user_id, username, password_hash, role)

    def add_resource(self, resource_id, campus_name, name, resource_type):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM resources WHERE resource_id = ?", (resource_id,))
            if cur.fetchone():
                raise ValueError(f"Resource ID '{resource_id}' already exists. IDs must be unique.")
            cur.execute("""
                INSERT INTO resources (resource_id, campus, name, resource_type)
                VALUES (?, ?, ?, ?)
            """, (resource_id, campus_name, name, resource_type))
            conn.commit()
        finally:
            conn.close()

    def update_resource(self, resource_id, new_name=None, new_type=None):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT name, resource_type FROM resources WHERE resource_id = ?", (resource_id,))
            row = cur.fetchone()
            if row is None:
                raise ValueError("Resource not found.")
            name = new_name if new_name else row[0]
            rtype = new_type if new_type else row[1]
            cur.execute(
                "UPDATE resources SET name = ?, resource_type = ? WHERE resource_id = ?",
                (name, rtype, resource_id),
            )
            conn.commit()
        finally:
            conn.close()

    def remove_resource(self, resource_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM resources WHERE resource_id = ?", (resource_id,))
        conn.commit()
        conn.close()

    def view_campus_resources(self, campus_name):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT resource_id, name, resource_type FROM resources WHERE campus = ? ORDER BY resource_id",
            (campus_name,),
        )
        rows = cur.fetchall()
        conn.close()
        return rows

    def view_campus_bookings(self, campus_name):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT b.booking_id, u.username, b.resource_id, b.date, b.start_time, b.duration_min, b.status
            FROM bookings b JOIN users u ON b.user_id = u.user_id
            WHERE b.campus = ? ORDER BY b.date, b.start_time
        """, (campus_name,))
        rows = cur.fetchall()
        conn.close()
        return rows

    def usage_trends(self, campus_name):
        """Return total active bookings, the most-used resource, and the
        average booking duration for this campus."""
        bookings = self.view_campus_bookings(campus_name)
        active = [b for b in bookings if b[6] == 'active']
        total = len(active)
        if total == 0:
            return {"total_bookings": 0, "most_used_resource": None, "avg_duration": 0}
        counts = Counter(b[2] for b in active)
        most_used = counts.most_common(1)[0][0]
        avg_duration = round(sum(b[5] for b in active) / total, 1)
        return {"total_bookings": total, "most_used_resource": most_used, "avg_duration": avg_duration}

"""
models/system_operator.py
System Operator role: institution-wide, cross-campus visibility used for
comparative reporting by management.
"""
from collections import Counter

from database import get_connection
from models.user import User
from models.campus import list_campus_names


class SystemOperator(User):
    def __init__(self, user_id, username, password_hash, role="operator"):
        super().__init__(user_id, username, password_hash, role)

    def all_bookings(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT b.booking_id, u.username, b.campus, b.resource_id, b.date, b.start_time, b.duration_min, b.status
            FROM bookings b JOIN users u ON b.user_id = u.user_id
            ORDER BY b.campus, b.date, b.start_time
        """)
        rows = cur.fetchall()
        conn.close()
        return rows

    def campus_comparison_report(self):
        """Return {campus_name: {total_bookings, most_used_resource,
        avg_duration}, ...} across every campus, for side-by-side
        comparison of usage trends."""
        report = {}
        bookings = self.all_bookings()
        for campus_name in list_campus_names():
            campus_bookings = [b for b in bookings if b[2] == campus_name and b[7] == 'active']
            total = len(campus_bookings)
            if total == 0:
                report[campus_name] = {"total_bookings": 0, "most_used_resource": "-", "avg_duration": 0}
                continue
            counts = Counter(b[3] for b in campus_bookings)
            most_used = counts.most_common(1)[0][0]
            avg_duration = round(sum(b[6] for b in campus_bookings) / total, 1)
            report[campus_name] = {
                "total_bookings": total,
                "most_used_resource": most_used,
                "avg_duration": avg_duration,
            }
        return report

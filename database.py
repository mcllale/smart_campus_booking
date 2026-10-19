"""
database.py
Handles SQLite connection creation and schema initialisation for the
Smart Campus Resource Booking System. Also seeds three campuses with
different booking policies so the system runs "out of the box", and a
handful of starter resources per campus.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "booking_system.db")


def get_connection():
    """Return a connection to the SQLite database (creates the file/folder
    the first time this is called)."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialise_database():
    """Create all tables if they do not already exist, and seed default
    campuses/resources so the booking-policy logic has data to work with.
    Safe to call every time the program starts (uses IF NOT EXISTS / OR IGNORE)."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,      -- stored as a SHA-256 hash, never plain text
            role TEXT NOT NULL           -- 'lecturer' | 'admin' | 'operator'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS campuses (
            campus_name TEXT PRIMARY KEY,
            max_duration INTEGER NOT NULL,       -- minutes, per booking
            open_hour INTEGER NOT NULL,          -- 24h clock, e.g. 8
            close_hour INTEGER NOT NULL,         -- 24h clock, e.g. 18
            max_bookings_per_day INTEGER,        -- NULL = unlimited per lecturer per day
            policy_description TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            resource_id TEXT PRIMARY KEY,        -- e.g. 'JHB-LAB-01', unique institution-wide
            campus TEXT NOT NULL,
            name TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            FOREIGN KEY (campus) REFERENCES campuses(campus_name)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            campus TEXT NOT NULL,
            date TEXT NOT NULL,                  -- 'YYYY-MM-DD'
            start_time TEXT NOT NULL,            -- 'HH:MM'
            duration_min INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',   -- 'active' | 'cancelled'
            FOREIGN KEY (resource_id) REFERENCES resources(resource_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    _seed_campuses(cur)
    _seed_resources(cur)

    conn.commit()
    conn.close()


def _seed_campuses(cur):
    """Three campuses, each with a genuinely different booking policy, so
    the "campus-specific rules" requirement is visibly satisfied."""
    campuses = [
        ("Johannesburg", 180, 8, 18, None,
         "Standard hours 08:00-18:00. Max 180 min per booking. "
         "No daily booking limit (first-come, first-served)."),
        ("Durban", 120, 7, 20, None,
         "Extended hours 07:00-20:00. Max 120 min per booking. "
         "Longer opening hours suit evening classes."),
        ("Cape Town", 90, 9, 17, 2,
         "Restricted hours 09:00-17:00. Max 90 min per booking. "
         "Each lecturer may make at most 2 bookings per day at this campus."),
    ]
    cur.executemany("""
        INSERT OR IGNORE INTO campuses
        (campus_name, max_duration, open_hour, close_hour, max_bookings_per_day, policy_description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, campuses)


def _seed_resources(cur):
    resources = [
        ("JHB-LAB-01", "Johannesburg", "Computer Lab 1", "Computer Lab"),
        ("JHB-LAB-02", "Johannesburg", "Computer Lab 2", "Computer Lab"),
        ("JHB-PROJ-01", "Johannesburg", "Projector A", "Projector"),
        ("JHB-SEM-01", "Johannesburg", "Seminar Room A", "Seminar Room"),
        ("DBN-LAB-01", "Durban", "Computer Lab 1", "Computer Lab"),
        ("DBN-PROJ-01", "Durban", "Projector A", "Projector"),
        ("DBN-SEM-01", "Durban", "Seminar Room A", "Seminar Room"),
        ("CPT-LAB-01", "Cape Town", "Computer Lab 1", "Computer Lab"),
        ("CPT-PROJ-01", "Cape Town", "Projector A", "Projector"),
        ("CPT-SEM-01", "Cape Town", "Seminar Room A", "Seminar Room"),
    ]
    cur.executemany("""
        INSERT OR IGNORE INTO resources (resource_id, campus, name, resource_type)
        VALUES (?, ?, ?, ?)
    """, resources)

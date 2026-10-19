"""
models/user.py
Base User class shared by Lecturer, CampusAdministrator and SystemOperator.
Demonstrates encapsulation (the password is never stored or compared in
plain text) and provides the shared registration/login behaviour used by
every role.
"""
import hashlib

from database import get_connection


def _hash_password(plain_text):
    """One-way hash so plain-text passwords are never stored or compared."""
    return hashlib.sha256(plain_text.encode("utf-8")).hexdigest()


class User:
    def __init__(self, user_id, username, password_hash, role):
        self.user_id = user_id
        self.username = username
        self._password = password_hash  # encapsulated - leading underscore
        self.role = role

    def check_password(self, entered_password):
        return self._password == _hash_password(entered_password)

    @staticmethod
    def register(username, plain_password, role):
        """Create a new user account. Returns the new user_id.
        Raises ValueError if the username already exists or the role is invalid."""
        if role not in ("lecturer", "admin", "operator"):
            raise ValueError(f"Unknown role: {role}")

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, _hash_password(plain_password), role),
            )
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            if "UNIQUE" in str(e):
                raise ValueError(f"Username '{username}' is already taken.")
            raise
        finally:
            conn.close()

    @staticmethod
    def authenticate(username, plain_password):
        """Look up a user by username and verify the password.
        Returns a role-specific User subclass instance, or None if the
        credentials are invalid."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, username, password, role FROM users WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
        conn.close()
        if row is None:
            return None

        user_id, uname, pwd_hash, role = row
        candidate = User(user_id, uname, pwd_hash, role)
        if not candidate.check_password(plain_password):
            return None

        # Deferred imports avoid a circular-import problem (the subclasses
        # import User from this module at the top of their own files).
        from models.lecturer import Lecturer
        from models.campus_administrator import CampusAdministrator
        from models.system_operator import SystemOperator

        role_classes = {
            "lecturer": Lecturer,
            "admin": CampusAdministrator,
            "operator": SystemOperator,
        }
        cls = role_classes.get(role)
        if cls is None:
            return candidate
        return cls(user_id, uname, pwd_hash, role)

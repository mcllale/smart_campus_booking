"""
models/validation.py
Reusable validation helpers for the GUI layer. Keeping validation logic
here (rather than scattered inside widget callbacks) means the same rules
are enforced consistently everywhere a form is submitted, and the GUI code
stays focused on layout instead of business rules.
"""
from datetime import date, datetime


def validate_registration_form(username, password, confirm_password):
    errors = []
    if not username or not username.strip():
        errors.append("Username is required.")
    if not password:
        errors.append("Password is required.")
    elif len(password) < 4:
        errors.append("Password must be at least 4 characters.")
    if password != confirm_password:
        errors.append("Passwords do not match.")
    return errors


def validate_login_form(username, password):
    errors = []
    if not username:
        errors.append("Username is required.")
    if not password:
        errors.append("Password is required.")
    return errors


def validate_booking_inputs(resource_id, date_str, start_time, duration_str):
    """Basic format-level checks before the booking is handed to the
    campus-policy and overlap logic (which raise their own, more specific
    ValueErrors)."""
    errors = []
    if not resource_id:
        errors.append("Please select a resource.")

    try:
        y, m, d = map(int, date_str.split("-"))
        if date(y, m, d) < date.today():
            errors.append("Date cannot be in the past.")
    except (ValueError, AttributeError):
        errors.append("Date must be in YYYY-MM-DD format.")

    try:
        datetime.strptime(start_time, "%H:%M")
    except (ValueError, TypeError):
        errors.append("Start time must be in HH:MM format (24-hour).")

    try:
        duration = int(duration_str)
        if duration <= 0:
            errors.append("Duration must be a positive number of minutes.")
    except (ValueError, TypeError):
        errors.append("Duration must be a whole number of minutes.")

    return errors


def validate_resource_form(resource_id, name, resource_type):
    errors = []
    if not resource_id or not resource_id.strip():
        errors.append("Resource ID is required.")
    if not name or not name.strip():
        errors.append("Resource name is required.")
    if not resource_type or not resource_type.strip():
        errors.append("Resource type is required.")
    return errors

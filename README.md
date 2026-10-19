# Smart Campus Resource Booking System

A desktop application (Tkinter GUI + SQLite database) built for Richfield
Graduate Institution to replace manual, spreadsheet/email-based booking of
shared academic resources (computer labs, projectors, seminar rooms) across
multiple campuses.

## Running the project

1. Make sure you have Python 3.9+ installed.
2. Tkinter is part of the Python standard library, but on Linux it's
   sometimes a separate OS package:
   ```
   sudo apt-get install python3-tk
   ```
3. From the project folder, run:
   ```
   python3 main.py
   ```
   On first run this automatically creates `data/booking_system.db`,
   builds all tables, and seeds three campuses (each with a different
   booking policy) plus a starting set of resources and demo accounts.

## Demo accounts

| Role                  | Username    | Password      |
|------------------------|------------|---------------|
| System Operator        | operator1  | operator123   |
| Campus Administrator   | admin_jhb  | admin123      |
| Campus Administrator   | admin_dbn  | admin123      |
| Campus Administrator   | admin_cpt  | admin123      |

Register a new lecturer account from the
"Register (Lecturer)" tab on the login screen.

## Project structure

```
smart_campus_booking/
|-- main.py                  # entry point: initialises DB, launches login screen
|-- database.py               # SQLite connection + schema + seed data
|-- requirements.txt
|-- models/
|   |-- user.py               # base User class (encapsulated password, auth)
|   |-- lecturer.py           # Lecturer(User): browse, book, view/cancel bookings
|   |-- campus_administrator.py  # CampusAdministrator(User): manage resources, trends
|   |-- system_operator.py    # SystemOperator(User): cross-campus reporting
|   |-- campus.py             # Campus class: policy rules live here, not in the GUI
|   |-- resource.py           # Resource data class
|   |-- booking.py            # Booking data class + overlap-checking logic
|   |-- validation.py         # form validation helpers used by the GUI
|-- gui/
|   |-- login_window.py       # login + lecturer self-registration
|   |-- booking_window.py     # Lecturer main window
|   |-- admin_window.py       # Campus Administrator main window
|   |-- reports_window.py     # System Operator main window
|-- data/
    |-- booking_system.db     # created automatically on first run
```

## How each requirement is met

- **Multiple campuses, structured data**: campuses and resources live in
  SQLite tables and are loaded into `Campus`/`Resource` objects; the active
  campus is always shown in the GUI header.
- **Role-based access, OOP**: `Lecturer`, `CampusAdministrator` and
  `SystemOperator` all inherit from `User` (encapsulated password hash,
  shared login logic). `User.authenticate()` returns the correct subclass
  automatically.
- **Campus-specific booking policies**: `Campus.validate_booking()` checks
  duration limits, allowed hours, and (for Cape Town) a daily-bookings cap
  — each campus has different values, defined once in `database.py` and
  read at runtime, so a new campus with new rules is a data change, not a
  code change.
- **Overlap prevention**: `models/booking.py: overlaps_existing()` checks
  any new booking against existing active bookings for that resource and
  date before it is inserted.
- **Persistence**: all users, campuses, resources and bookings are stored
  in `data/booking_system.db` and survive program restarts.
- **Reporting**: `CampusAdministrator.usage_trends()` gives per-campus
  totals/most-used-resource/average duration; `SystemOperator
  .campus_comparison_report()` gives the same metrics side-by-side across
  every campus.
- **Validation & error handling**: `models/validation.py` checks form
  input before it ever reaches the database layer; `Campus
  .validate_booking()` and the overlap check raise `ValueError`s with
  clear messages that the GUI displays inline instead of crashing.

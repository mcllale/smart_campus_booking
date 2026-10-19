# Smart Campus Resource Booking System

A desktop application (Tkinter GUI + SQLite database) built for Richfield
Graduate Institution to replace manual, spreadsheet/email-based booking of
shared academic resources (computer labs, projectors, seminar rooms) across
multiple campuses.

## Background

Richfield Graduate Institution is operating across multiple campuses in South Africa and relies heavily 
on shared academic resources such as computer laboratories, multimedia projectors, seminar rooms, and 
presentation equipment. These resources are essential for daily teaching, assessments, and academic 
events. 
At present, each campus manages resource bookings manually through email requests, spreadsheets, or 
paper-based registers. This fragmented approach has led to frequent problems, including double 
bookings, underutilisation of resources, lack of accountability, and difficulty generating accurate usage 
reports. Additionally, management has no centralised view of how resources are being used across 
campuses. 
To address these challenges, the institution has requested the development of a **Smart Campus 
Resource Booking System** using Python. The system must provide a consistent, reliable, and user
friendly solution that supports multiple campuses, enforces booking rules, and stores data persistently for 
reporting and analysis.

## System Overview
The system:   
- Support multiple campuses using structured data collections such as lists, dictionaries, and sets.  
- Provide user authentication and role-based access control using object-oriented design principles.  
- Allow users to manage and interact with campus resources through a graphical user interface built 
using Tkinter.  
- Track resource availability, bookings, and usage duration accurately.  
- Persist all system data using an SQLite database so that information is retained between program 
runs.

## User Roles and Access Control  
The system support three distinct user roles, implemented using object-oriented programming 
concepts such as classes, inheritance, and encapsulation.  

### 1. Lecturer  

A lecturer represents an academic staff member who books resources for teaching or presentations. They can:  
- Register an account and log into the system using a GUI-based login interface.
- Select a campus and view available resources stored using dictionaries or lists.  
- Create a booking for a selected resource, date, and time.  
- View their personal booking history retrieved from the database.  

### 2. Campus Administrator  

A campus administrator manages resources at a specific campus. They can:  
- Log in to the system with administrator privileges.  
- Add, update, and remove campus resources using appropriate data structures.  
- View all bookings associated with their campus.  
- Monitor resource availability and usage trends.  

### 3. System Operator  
A system operator represents institutional management with system-wide access. They can:  
- Log in to the system with full access rights.
- View booking and resource data across all campuses.  
- Generate comparative reports across all campuses.  



## Running the project

1. Make sure you have Python 3.9+ installed.
2. Tkinter is part of the Python standard library, but on Linux it's
   sometimes a separate OS package:
   ```
   sudo apt-get install python3-tk
   ```
3. From the project folder, run:
   ```
   python main.py
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

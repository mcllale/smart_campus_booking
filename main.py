'''
The main entry point for the Smart Campus Resource Booking System application.
It initializes the database, ensures that demo accounts exist, and launches the login window.
'''
from database import initialise_database
from models.user import User
from gui.login_window import LoginWindow


def _ensure_demo_accounts():
    '''
    Create default admin/operator accounts on first run only, so the
    system is usable immediately without any manual database setup.
    Lecturers self-register from the login screen instead.
    '''
    demo_accounts = [
        ("operator1", "operator123", "operator"),
        ("admin_jhb", "admin123", "admin"),
        ("admin_dbn", "admin123", "admin"),
        ("admin_cpt", "admin123", "admin"),
    ]

    # Create demo accounts if they don't already exist
    for username, password, role in demo_accounts:
        try:
            User.register(username, password, role)
        except ValueError:
            pass  # account already exists from a previous run - fine


def main():
    '''
    The main entry point for the application. It initialises the database,
    ensures demo accounts exist, and launches the login window.
    '''
    initialise_database()
    _ensure_demo_accounts()
    app = LoginWindow()
    app.mainloop()


if __name__ == "__main__":
    main()

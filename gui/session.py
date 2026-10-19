"""
gui/session.py
Tiny shared helper so every role's main window can log out the same way:
close the current window and return to the login screen.
"""


def logout(current_window):
    """Destroy the current window and reopen the login screen."""
    current_window.destroy()
    from gui.login_window import LoginWindow
    LoginWindow().mainloop()

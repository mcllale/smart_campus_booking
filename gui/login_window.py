"""
gui/login_window.py
The application's entry screen: lets an existing user log in, or a new
lecturer self-register. On success, opens the role-appropriate main window.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from gui.booking_window import LecturerMainWindow
from gui.admin_window import AdminMainWindow
from gui.reports_window import OperatorMainWindow

from models.user import User
from models.validation import validate_login_form, validate_registration_form


class LoginWindow(tk.Tk):
    '''
    The login window allows users to log in or register as a lecturer.
    It provides two tabs: one for logging in and
    another for registering a new lecturer account.
    '''
    def __init__(self):
        super().__init__()
        self.title("Smart Campus Resource Booking System - Login")
        self.geometry("440x360")
        self.resizable(False, False)
        self._build_tabs()

    def _build_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        login_frame = ttk.Frame(notebook, padding=20)
        register_frame = ttk.Frame(notebook, padding=20)
        notebook.add(login_frame, text="Log In")
        notebook.add(register_frame, text="Register (Lecturer)")

        self._build_login_form(login_frame)
        self._build_register_form(register_frame)

    def _build_login_form(self, frame):
        ttk.Label(frame, text="Username").grid(row=0, column=0, sticky="w", pady=6)
        username_entry = ttk.Entry(frame, width=26)
        username_entry.grid(row=0, column=1, pady=6)

        ttk.Label(frame, text="Password").grid(row=1, column=0, sticky="w", pady=6)
        password_entry = ttk.Entry(frame, width=26, show="*")
        password_entry.grid(row=1, column=1, pady=6)

        error_label = ttk.Label(frame, foreground="red", wraplength=340)
        error_label.grid(row=2, column=0, columnspan=2, pady=6)

        def on_login():
            username = username_entry.get().strip()
            password = password_entry.get()
            errors = validate_login_form(username, password)
            if errors:
                error_label.config(text=errors[0])
                return
            user = User.authenticate(username, password)
            if user is None:
                error_label.config(text="Invalid username or password.")
                return
            self.destroy()
            _launch_role_window(user)

        password_entry.bind("<Return>", lambda e: on_login())
        ttk.Button(frame, text="Log In", command=on_login).grid(row=3,
                                                                column=0,
                                                                columnspan=2,
                                                                pady=16)

        ttk.Label(frame, foreground="gray", justify="left").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=10
        )

    def _build_register_form(self, frame):
        ttk.Label(frame, text="Choose a username").grid(row=0,
                                                        column=0,
                                                        sticky="w",
                                                        pady=6)
        username_entry = ttk.Entry(frame, width=26)
        username_entry.grid(row=0, column=1, pady=6)

        ttk.Label(frame, text="Choose a password").grid(row=1,
                                                        column=0,
                                                        sticky="w",
                                                        pady=6)
        password_entry = ttk.Entry(frame, width=26, show="*")
        password_entry.grid(row=1, column=1, pady=6)

        ttk.Label(frame, text="Confirm password").grid(row=2,
                                                       column=0,
                                                       sticky="w",
                                                       pady=6)
        confirm_entry = ttk.Entry(frame, width=26, show="*")
        confirm_entry.grid(row=2, column=1, pady=6)

        error_label = ttk.Label(frame, foreground="red", wraplength=340)
        error_label.grid(row=3, column=0, columnspan=2, pady=6)

        def on_register():
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm = confirm_entry.get()
            errors = validate_registration_form(username, password, confirm)
            if errors:
                error_label.config(text=errors[0])
                return
            try:
                User.register(username, password, role="lecturer")
            except ValueError as e:
                error_label.config(text=str(e))
                return
            messagebox.showinfo("Account created", "You can now log in as a lecturer.")
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            confirm_entry.delete(0, tk.END)
            error_label.config(text="")

        ttk.Button(frame, text="Register", command=on_register).grid(row=4,
                                                                     column=0,
                                                                     columnspan=2,
                                                                     pady=16)

        note = (
            "Note: Campus Administrator and System Operator accounts are "
            "provisioned by the institution rather than self-registered. "
            "Demo credentials for those roles are on the Log In tab."
        )
        ttk.Label(frame, text=note, wraplength=340, foreground="gray", justify="left").grid(
            row=5, column=0, columnspan=2, pady=10
        )


def _launch_role_window(user):
    if user.role == "lecturer":
        LecturerMainWindow(user).mainloop()
    elif user.role == "admin":
        AdminMainWindow(user).mainloop()
    elif user.role == "operator":
        OperatorMainWindow(user).mainloop()
    else:
        messagebox.showerror("Error", f"Unknown role: {user.role}")

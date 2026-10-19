"""
gui/booking_window.py
Main window for the Lecturer role: choose a campus, see its active
booking policy, browse available resources, submit a booking, and manage
existing bookings.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from models.campus import list_campus_names, get_campus
from models.validation import validate_booking_inputs
from gui.session import logout


class LecturerMainWindow(tk.Tk):
    def __init__(self, lecturer):
        super().__init__()
        self.lecturer = lecturer
        self.title(f"Smart Campus Booking - Lecturer: {lecturer.username}")
        self.geometry("800x580")

        self.campus_var = tk.StringVar()
        self._build_layout()

        campuses = list_campus_names()
        if campuses:
            self.campus_var.set(campuses[0])
            self._on_campus_change()

    def _build_layout(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Active Campus:", font=("Segoe UI", 10, "bold")).pack(side="left")
        campus_combo = ttk.Combobox(
            top, textvariable=self.campus_var, values=list_campus_names(),
            state="readonly", width=18,
        )
        campus_combo.pack(side="left", padx=8)
        campus_combo.bind("<<ComboboxSelected>>", lambda e: self._on_campus_change())

        self.policy_label = ttk.Label(top, text="", foreground="#227722", wraplength=540, justify="left")
        self.policy_label.pack(side="left", padx=15)

        ttk.Button(top, text="Log Out", command=lambda: logout(self)).pack(side="right")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.book_tab = ttk.Frame(notebook, padding=10)
        self.history_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.book_tab, text="Book a Resource")
        notebook.add(self.history_tab, text="My Bookings")
        notebook.bind("<<NotebookTabChanged>>", lambda e: self._refresh_history())

        self._build_booking_tab()
        self._build_history_tab()

    # ---------- Booking tab ----------
    def _build_booking_tab(self):
        form = ttk.Frame(self.book_tab)
        form.pack(fill="x")

        ttk.Label(form, text="Resource").grid(row=0, column=0, sticky="w", pady=6)
        self.resource_cb = ttk.Combobox(form, state="readonly", width=28)
        self.resource_cb.grid(row=0, column=1, pady=6, sticky="w")

        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(row=1, column=0, sticky="w", pady=6)
        self.date_entry = ttk.Entry(form, width=30)
        self.date_entry.grid(row=1, column=1, pady=6, sticky="w")

        ttk.Label(form, text="Start Time (HH:MM)").grid(row=2, column=0, sticky="w", pady=6)
        self.time_entry = ttk.Entry(form, width=30)
        self.time_entry.grid(row=2, column=1, pady=6, sticky="w")

        ttk.Label(form, text="Duration (minutes)").grid(row=3, column=0, sticky="w", pady=6)
        self.duration_spin = ttk.Spinbox(form, from_=15, to=999, increment=15, width=28)
        self.duration_spin.grid(row=3, column=1, pady=6, sticky="w")
        self.duration_spin.set(30)

        self.error_label = ttk.Label(form, text="", foreground="red", wraplength=520)
        self.error_label.grid(row=4, column=0, columnspan=2, pady=8, sticky="w")

        ttk.Button(form, text="Book Resource", command=self._on_submit).grid(
            row=5, column=0, columnspan=2, pady=10
        )

        ttk.Separator(self.book_tab).pack(fill="x", pady=10)
        ttk.Label(self.book_tab, text="Resources at this campus:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.availability_list = tk.Listbox(self.book_tab, height=8)
        self.availability_list.pack(fill="both", expand=True, pady=6)

    def _on_campus_change(self):
        campus_name = self.campus_var.get()
        campus = get_campus(campus_name)
        self.policy_label.config(text=f"Policy: {campus.policy_description}")
        self._refresh_resources()
        self._refresh_history()

    def _refresh_resources(self):
        rows = self.lecturer.view_available_resources(self.campus_var.get())
        resource_ids = [r[0] for r in rows]
        self.resource_cb["values"] = resource_ids
        if resource_ids:
            self.resource_cb.set(resource_ids[0])
        else:
            self.resource_cb.set("")

        self.availability_list.delete(0, tk.END)
        for resource_id, name, rtype in rows:
            self.availability_list.insert(tk.END, f"{resource_id}  -  {name}  ({rtype})")

    def _on_submit(self):
        campus_name = self.campus_var.get()
        resource_id = self.resource_cb.get()
        date_str = self.date_entry.get().strip()
        start_time = self.time_entry.get().strip()
        duration_str = self.duration_spin.get()

        errors = validate_booking_inputs(resource_id, date_str, start_time, duration_str)
        if errors:
            self.error_label.config(text=errors[0])
            return

        try:
            self.lecturer.book_resource(campus_name, resource_id, date_str, start_time, int(duration_str))
        except ValueError as e:
            self.error_label.config(text=str(e))
            return

        self.error_label.config(text="")
        messagebox.showinfo("Booked", "Your booking was created successfully.")
        self._refresh_history()

    # ---------- History tab ----------
    def _build_history_tab(self):
        columns = ("id", "resource", "campus", "date", "time", "duration", "status")
        self.history_tree = ttk.Treeview(self.history_tab, columns=columns, show="headings", height=15)
        headings = ["ID", "Resource", "Campus", "Date", "Start", "Duration (min)", "Status"]
        for col, heading in zip(columns, headings):
            self.history_tree.heading(col, text=heading)
            self.history_tree.column(col, width=100, anchor="center")
        self.history_tree.pack(fill="both", expand=True)

        ttk.Button(self.history_tab, text="Cancel Selected Booking", command=self._on_cancel).pack(pady=10)

    def _refresh_history(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        for booking in self.lecturer.view_my_bookings():
            self.history_tree.insert("", tk.END, values=booking)

    def _on_cancel(self):
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a booking to cancel first.")
            return
        booking_id = self.history_tree.item(selected[0])["values"][0]
        try:
            self.lecturer.cancel_booking(booking_id)
        except ValueError as e:
            messagebox.showerror("Cannot cancel", str(e))
            return
        self._refresh_history()

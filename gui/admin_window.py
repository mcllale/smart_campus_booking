"""
gui/admin_window.py
Main window for the Campus Administrator role: manage resources for the
selected campus, view all bookings there, and see usage trends.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from models.campus import list_campus_names
from models.validation import validate_resource_form
from gui.session import logout


class AdminMainWindow(tk.Tk):
    def __init__(self, admin):
        super().__init__()
        self.admin = admin
        self.title(f"Smart Campus Booking - Administrator: {admin.username}")
        self.geometry("860x620")

        self.campus_var = tk.StringVar()
        self._build_layout()

        campuses = list_campus_names()
        if campuses:
            self.campus_var.set(campuses[0])
            self._refresh_all()

    def _build_layout(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Managing Campus:", font=("Segoe UI", 10, "bold")).pack(side="left")
        combo = ttk.Combobox(
            top, textvariable=self.campus_var, values=list_campus_names(),
            state="readonly", width=18,
        )
        combo.pack(side="left", padx=8)
        combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_all())

        ttk.Button(top, text="Log Out", command=lambda: logout(self)).pack(side="right")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.resources_tab = ttk.Frame(notebook, padding=10)
        self.bookings_tab = ttk.Frame(notebook, padding=10)
        self.trends_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.resources_tab, text="Manage Resources")
        notebook.add(self.bookings_tab, text="Campus Bookings")
        notebook.add(self.trends_tab, text="Usage Trends")

        self._build_resources_tab()
        self._build_bookings_tab()
        self._build_trends_tab()

    # ---------- Resources ----------
    def _build_resources_tab(self):
        form = ttk.Frame(self.resources_tab)
        form.pack(fill="x")

        ttk.Label(form, text="Resource ID").grid(row=0, column=0, sticky="w")
        self.id_entry = ttk.Entry(form, width=16)
        self.id_entry.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(form, text="Name").grid(row=0, column=2, sticky="w")
        self.name_entry = ttk.Entry(form, width=20)
        self.name_entry.grid(row=0, column=3, padx=5, pady=4)

        ttk.Label(form, text="Type").grid(row=0, column=4, sticky="w")
        self.type_entry = ttk.Entry(form, width=16)
        self.type_entry.grid(row=0, column=5, padx=5, pady=4)

        self.resource_error = ttk.Label(self.resources_tab, foreground="red")
        self.resource_error.pack(anchor="w", pady=4)

        btns = ttk.Frame(self.resources_tab)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="Add", command=self._on_add_resource).pack(side="left", padx=4)
        ttk.Button(btns, text="Update Selected", command=self._on_update_resource).pack(side="left", padx=4)
        ttk.Button(btns, text="Remove Selected", command=self._on_remove_resource).pack(side="left", padx=4)
        ttk.Button(btns, text="Clear Form", command=self._clear_resource_form).pack(side="left", padx=4)

        columns = ("id", "name", "type")
        self.resource_tree = ttk.Treeview(self.resources_tab, columns=columns, show="headings", height=14)
        for col, heading in zip(columns, ["Resource ID", "Name", "Type"]):
            self.resource_tree.heading(col, text=heading)
        self.resource_tree.pack(fill="both", expand=True, pady=8)
        self.resource_tree.bind("<<TreeviewSelect>>", self._on_select_resource)

    def _clear_resource_form(self):
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.type_entry.delete(0, tk.END)
        self.resource_error.config(text="")

    def _on_select_resource(self, event):
        selected = self.resource_tree.selection()
        if not selected:
            return
        values = self.resource_tree.item(selected[0])["values"]
        self.id_entry.delete(0, tk.END); self.id_entry.insert(0, values[0])
        self.name_entry.delete(0, tk.END); self.name_entry.insert(0, values[1])
        self.type_entry.delete(0, tk.END); self.type_entry.insert(0, values[2])

    def _on_add_resource(self):
        resource_id = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        rtype = self.type_entry.get().strip()
        errors = validate_resource_form(resource_id, name, rtype)
        if errors:
            self.resource_error.config(text=errors[0])
            return
        try:
            self.admin.add_resource(resource_id, self.campus_var.get(), name, rtype)
        except ValueError as e:
            self.resource_error.config(text=str(e))
            return
        self.resource_error.config(text="")
        self._clear_resource_form()
        self._refresh_all()

    def _on_update_resource(self):
        resource_id = self.id_entry.get().strip()
        if not resource_id:
            self.resource_error.config(text="Select a resource to update first.")
            return
        try:
            self.admin.update_resource(resource_id, self.name_entry.get().strip(), self.type_entry.get().strip())
        except ValueError as e:
            self.resource_error.config(text=str(e))
            return
        self.resource_error.config(text="")
        self._refresh_all()

    def _on_remove_resource(self):
        selected = self.resource_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a resource to remove first.")
            return
        resource_id = self.resource_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm", f"Remove resource '{resource_id}'? This cannot be undone."):
            self.admin.remove_resource(resource_id)
            self._clear_resource_form()
            self._refresh_all()

    # ---------- Bookings ----------
    def _build_bookings_tab(self):
        columns = ("id", "lecturer", "resource", "date", "time", "duration", "status")
        self.bookings_tree = ttk.Treeview(self.bookings_tab, columns=columns, show="headings", height=18)
        headings = ["ID", "Lecturer", "Resource", "Date", "Start", "Duration (min)", "Status"]
        for col, heading in zip(columns, headings):
            self.bookings_tree.heading(col, text=heading)
        self.bookings_tree.pack(fill="both", expand=True)

    # ---------- Trends ----------
    def _build_trends_tab(self):
        self.trends_label = ttk.Label(self.trends_tab, font=("Segoe UI", 11), justify="left")
        self.trends_label.pack(anchor="w", pady=10)

    def _refresh_all(self):
        campus_name = self.campus_var.get()

        for row in self.resource_tree.get_children():
            self.resource_tree.delete(row)
        for r in self.admin.view_campus_resources(campus_name):
            self.resource_tree.insert("", tk.END, values=r)

        for row in self.bookings_tree.get_children():
            self.bookings_tree.delete(row)
        for b in self.admin.view_campus_bookings(campus_name):
            self.bookings_tree.insert("", tk.END, values=b)

        trends = self.admin.usage_trends(campus_name)
        self.trends_label.config(text=(
            f"Total active bookings: {trends['total_bookings']}\n"
            f"Most frequently used resource: {trends['most_used_resource'] or '-'}\n"
            f"Average booking duration: {trends['avg_duration']} minutes"
        ))

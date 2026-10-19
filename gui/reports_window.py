"""
gui/reports_window.py
Main window for the System Operator role: institution-wide visibility
into every booking, plus a side-by-side comparison of campus usage trends.
"""
import tkinter as tk
from tkinter import ttk

from gui.session import logout


class OperatorMainWindow(tk.Tk):
    def __init__(self, operator):
        super().__init__()
        self.operator = operator
        self.title(f"Smart Campus Booking - System Operator: {operator.username}")
        self.geometry("900x600")

        top = ttk.Frame(self, padding=(10, 10, 10, 0))
        top.pack(fill="x")
        ttk.Label(top, text=f"Logged in as: {operator.username}", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(top, text="Log Out", command=lambda: logout(self)).pack(side="right")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.all_tab = ttk.Frame(notebook, padding=10)
        self.compare_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.all_tab, text="All Bookings")
        notebook.add(self.compare_tab, text="Cross-Campus Comparison")
        notebook.bind("<<NotebookTabChanged>>", lambda e: self._refresh())

        self._build_all_tab()
        self._build_compare_tab()
        self._refresh()

    def _build_all_tab(self):
        columns = ("id", "lecturer", "campus", "resource", "date", "time", "duration", "status")
        self.all_tree = ttk.Treeview(self.all_tab, columns=columns, show="headings", height=20)
        headings = ["ID", "Lecturer", "Campus", "Resource", "Date", "Start", "Duration (min)", "Status"]
        for col, heading in zip(columns, headings):
            self.all_tree.heading(col, text=heading)
        self.all_tree.pack(fill="both", expand=True)

    def _build_compare_tab(self):
        ttk.Label(
            self.compare_tab,
            text="Booking volume and behaviour differ across campuses partly because "
                 "each campus enforces different booking rules (see each admin's policy).",
            wraplength=800, foreground="gray",
        ).pack(anchor="w", pady=(0, 10))

        columns = ("campus", "total", "most_used", "avg_duration")
        self.compare_tree = ttk.Treeview(self.compare_tab, columns=columns, show="headings", height=10)
        headings = ["Campus", "Total Bookings", "Most Used Resource", "Avg Duration (min)"]
        for col, heading in zip(columns, headings):
            self.compare_tree.heading(col, text=heading)
        self.compare_tree.pack(fill="both", expand=True)

    def _refresh(self):
        for row in self.all_tree.get_children():
            self.all_tree.delete(row)
        for b in self.operator.all_bookings():
            self.all_tree.insert("", tk.END, values=b)

        for row in self.compare_tree.get_children():
            self.compare_tree.delete(row)
        report = self.operator.campus_comparison_report()
        for campus_name, stats in report.items():
            self.compare_tree.insert("", tk.END, values=(
                campus_name, stats["total_bookings"], stats["most_used_resource"], stats["avg_duration"]
            ))

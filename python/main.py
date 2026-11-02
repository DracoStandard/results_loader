"""Entry point / main window, ported from MainWindow.xaml(.cs)."""
import os
from datetime import date
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import comp_results
import csv_loader
import db

DEFAULT_CSV_DIR = os.path.expanduser(r"~\OneDrive\MEG Rankings\resultsForUpload")


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Results Loader")
        self.geometry("480x300")
        self.resizable(False, False)

        frm = ttk.Frame(self, padding=15)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Competition name:").grid(row=0, column=0, sticky="w")
        self.comp_name_var = tk.StringVar(value="Comp")
        ttk.Entry(frm, textvariable=self.comp_name_var, width=30).grid(
            row=0, column=1, sticky="w", pady=5
        )

        ttk.Label(frm, text="System:").grid(row=1, column=0, sticky="w")
        self.system_var = tk.StringVar(value="MEG")
        ttk.Entry(frm, textvariable=self.system_var, width=15).grid(
            row=1, column=1, sticky="w", pady=5
        )

        self.major_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Major", variable=self.major_var).grid(
            row=2, column=0, sticky="w", pady=5
        )

        ttk.Button(frm, text="Load Results CSV...", command=self.load_results).grid(
            row=3, column=0, columnspan=2, sticky="we", pady=(15, 5)
        )
        ttk.Button(
            frm, text="Fix Incorrect Army IDs", command=self.fix_army_ids
        ).grid(row=4, column=0, columnspan=2, sticky="we", pady=5)
        ttk.Button(
            frm, text="Update Old Comps", command=self.update_old_comps
        ).grid(row=5, column=0, columnspan=2, sticky="we", pady=5)

        self.status_var = tk.StringVar(value="")
        ttk.Label(frm, textvariable=self.status_var, foreground="gray", wraplength=440).grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(15, 0)
        )

    def load_results(self):
        initial_dir = DEFAULT_CSV_DIR if os.path.isdir(DEFAULT_CSV_DIR) else os.path.expanduser("~")
        path = filedialog.askopenfilename(
            initialdir=initial_dir, filetypes=[("CSV files", "*.csv")]
        )
        if not path:
            return

        comp_name = self.comp_name_var.get()
        system = self.system_var.get()
        is_major = self.major_var.get()

        try:
            rows = csv_loader.load_results_csv(path)
            processed, skipped = comp_results.process_results_csv(
                self, comp_name, date.today(), system, is_major, rows
            )
        except Exception as exc:
            messagebox.showerror(
                "Error",
                "Failed to load results:\n"
                f"{exc}\n\n"
                f"Details:\n{traceback.format_exc()}"
            )
            return

        self.status_var.set(f"Loaded {processed} placing(s), skipped {skipped} row(s).")
        messagebox.showinfo(
            "Done",
            f"Loaded {processed} placing(s) for '{comp_name}'.\n"
            f"Skipped {skipped} row(s) with an invalid position.",
        )

    def fix_army_ids(self):
        try:
            fixed = comp_results.fix_incorrect_army_ids(self)
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to fix army IDs:\n{exc}")
            return
        messagebox.showinfo(
            "Operation Complete", f"Incorrect Army IDs have been fixed ({fixed} updated)."
        )

    def update_old_comps(self):
        try:
            db.exec_update_old_comps()
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to update old comps:\n{exc}")
            return
        messagebox.showinfo("Update Complete", "Old competitions updated.")


if __name__ == "__main__":
    MainWindow().mainloop()

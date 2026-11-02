"""Modal picker dialog, equivalent to Window1.xaml.cs: shown when a player
or army name has no exact match, listing the closest fuzzy matches so the
user can confirm one or reject all of them.
"""
import tkinter as tk
from tkinter import ttk


class PickerDialog(tk.Toplevel):
    def __init__(self, parent, prompt_name, matches, id_header="ID", label_header="Name"):
        super().__init__(parent)
        self.title("Confirm match")
        self.resizable(False, False)
        self.result_id = None
        self.transient(parent)

        tk.Label(
            self,
            text=f'No exact match for "{prompt_name}". Choose the closest match, or None:',
            wraplength=360,
            justify="left",
        ).pack(padx=10, pady=(10, 5), anchor="w")

        columns = (id_header, label_header, "Score")
        self.tree = ttk.Treeview(
            self, columns=columns, show="headings", height=min(len(matches), 11)
        )
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140 if col != "Score" else 60, anchor="w")
        for cid, label, score in matches:
            self.tree.insert("", "end", iid=str(cid), values=(cid, label, f"{score:.0f}"))
        self.tree.pack(padx=10, pady=5, fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=(0, 10))
        self.yes_btn = tk.Button(
            btn_frame, text="Use Selected", state="disabled", command=self._on_yes
        )
        self.yes_btn.pack(side="left", padx=5)
        tk.Button(btn_frame, text="None of these", command=self._on_no).pack(
            side="left", padx=5
        )

        self.protocol("WM_DELETE_WINDOW", self._on_no)
        self.grab_set()
        self.focus_set()

    def _on_select(self, _event):
        self.yes_btn.config(state="normal")

    def _on_yes(self):
        sel = self.tree.selection()
        if sel:
            self.result_id = sel[0]
        self.destroy()

    def _on_no(self):
        self.result_id = None
        self.destroy()


def ask_pick(parent, prompt_name, matches, id_header="ID", label_header="Name"):
    """Blocks until the user picks a match or dismisses the dialog.
    Returns the chosen id as a string, or None.
    """
    dialog = PickerDialog(parent, prompt_name, matches, id_header, label_header)
    parent.wait_window(dialog)
    return dialog.result_id

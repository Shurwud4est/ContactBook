"""
ContactBook_GUI.py
------------------
A polished GUI-based Contact Book application built with tkinter.
Allows users to open any JSON contact file via a file dialog,
then add, view, search, and delete contacts.

Requirements: Python 3.x (no third-party libraries needed — tkinter is built-in)
"""

import json
import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# ─────────────────────────────────────────────
# COLOUR PALETTE & STYLE CONSTANTS
# ─────────────────────────────────────────────

BG         = "#0F1117"      # Near-black background
SURFACE    = "#1A1D27"      # Card / panel surface
SURFACE2   = "#22263A"      # Input fields, lighter surface
BORDER     = "#2E3350"      # Subtle borders
ACCENT     = "#5B7FFF"      # Primary accent (blue-violet)
ACCENT2    = "#3DFFB8"      # Secondary accent (teal-mint)
DANGER     = "#FF5C7A"      # Delete / error red-pink
TEXT       = "#E8EAF6"      # Primary text
TEXT_DIM   = "#7B85B4"      # Muted / placeholder text
TEXT_TITLE = "#FFFFFF"      # Titles / headers

FONT_TITLE  = ("Georgia", 22, "bold")
FONT_HEAD   = ("Georgia", 13, "bold")
FONT_LABEL  = ("Courier New", 10, "bold")
FONT_INPUT  = ("Courier New", 11)
FONT_BODY   = ("Courier New", 10)
FONT_BTN    = ("Georgia", 10, "bold")
FONT_SMALL  = ("Courier New", 9)


# ─────────────────────────────────────────────
# VALIDATION HELPERS
# ─────────────────────────────────────────────

def is_valid_name(name):
    return bool(re.fullmatch(r"[A-Za-z ]+", name))

def is_valid_phone(phone):
    return bool(re.fullmatch(r"\d+", phone))

def is_valid_email(email):
    return bool(re.fullmatch(r"[^@]+@[^@]+\.[A-Za-z]{2,4}", email))


# ─────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────

class ContactBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Book")
        self.root.geometry("980x680")
        self.root.minsize(820, 580)
        self.root.configure(bg=BG)

        self.contacts       = []
        self.contacts_file  = None          # Path of the currently open JSON
        self.filtered       = []            # Contacts shown in the list
        self.selected_index = None          # Index inside self.filtered

        self._build_ui()
        self._refresh_list()

    # ──────────────────────────────────────────
    # UI CONSTRUCTION
    # ──────────────────────────────────────────

    def _build_ui(self):
        # ── Top bar ───────────────────────────
        top = tk.Frame(self.root, bg=SURFACE, pady=0)
        top.pack(fill="x", side="top")

        # decorative accent line at very top
        tk.Frame(top, bg=ACCENT, height=3).pack(fill="x")

        header_row = tk.Frame(top, bg=SURFACE, padx=24, pady=14)
        header_row.pack(fill="x")

        tk.Label(
            header_row, text="◈  CONTACT BOOK",
            font=FONT_TITLE, fg=TEXT_TITLE, bg=SURFACE
        ).pack(side="left")

        # File-path indicator
        self.file_label = tk.Label(
            header_row, text="No file open",
            font=FONT_SMALL, fg=TEXT_DIM, bg=SURFACE
        )
        self.file_label.pack(side="left", padx=(18, 0), pady=(6, 0))

        # Open-file button (top-right)
        self._btn(header_row, "⊕  Open JSON File", self._open_file,
                  bg=ACCENT, fg=TEXT_TITLE).pack(side="right")

        # ── Main content area ─────────────────
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=0, pady=0)

        # Left panel — contact list + search
        left = tk.Frame(main, bg=SURFACE, width=320)
        left.pack(fill="y", side="left")
        left.pack_propagate(False)

        # Decorative accent stripe on left edge
        tk.Frame(left, bg=ACCENT2, width=3).pack(fill="y", side="left")

        left_inner = tk.Frame(left, bg=SURFACE)
        left_inner.pack(fill="both", expand=True)

        # search bar
        search_frame = tk.Frame(left_inner, bg=SURFACE, padx=14, pady=12)
        search_frame.pack(fill="x")

        tk.Label(search_frame, text="SEARCH", font=FONT_LABEL,
                 fg=ACCENT2, bg=SURFACE).pack(anchor="w")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._do_search())
        search_entry = tk.Entry(
            search_frame, textvariable=self.search_var,
            font=FONT_INPUT, bg=SURFACE2, fg=TEXT, insertbackground=TEXT,
            relief="flat", bd=0, highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=ACCENT
        )
        search_entry.pack(fill="x", pady=(6, 0), ipady=7, ipadx=6)

        tk.Frame(left_inner, bg=BORDER, height=1).pack(fill="x", pady=(8, 0))

        # Contact listbox
        list_frame = tk.Frame(left_inner, bg=SURFACE)
        list_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.listbox = tk.Listbox(
            list_frame,
            font=FONT_BODY, bg=SURFACE, fg=TEXT,
            selectbackground=ACCENT, selectforeground=TEXT_TITLE,
            activestyle="none", relief="flat", bd=0,
            highlightthickness=0, cursor="hand2",
            selectmode="single"
        )
        self.listbox.pack(fill="both", expand=True, side="left")
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        sb = tk.Scrollbar(list_frame, orient="vertical",
                          command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=sb.set)

        # count label
        self.count_label = tk.Label(
            left_inner, text="0 contacts",
            font=FONT_SMALL, fg=TEXT_DIM, bg=SURFACE, pady=6
        )
        self.count_label.pack()

        # Right panel — detail + form
        right = tk.Frame(main, bg=BG)
        right.pack(fill="both", expand=True, side="right")

        # ── Detail pane (shown when contact selected) ──
        self.detail_frame = tk.Frame(right, bg=BG)
        self.detail_frame.pack(fill="both", expand=True, padx=28, pady=24)

        self._build_detail_pane(self.detail_frame)
        self._build_form_pane(right)

    # ─── Detail pane ──────────────────────────
    def _build_detail_pane(self, parent):
        self.detail_card = tk.Frame(parent, bg=SURFACE, padx=28, pady=28)
        # Accent top line on card
        tk.Frame(self.detail_card, bg=ACCENT, height=3).pack(fill="x")

        inner = tk.Frame(self.detail_card, bg=SURFACE)
        inner.pack(fill="both", expand=True, pady=(18, 0))

        self.detail_name = tk.Label(
            inner, text="", font=("Georgia", 20, "bold"),
            fg=TEXT_TITLE, bg=SURFACE, anchor="w"
        )
        self.detail_name.pack(fill="x", pady=(0, 16))

        self.detail_fields = {}
        for field, icon in [("phone", "☎"), ("address", "⌂"), ("email", "✉")]:
            row = tk.Frame(inner, bg=SURFACE)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=icon, font=("Georgia", 16), fg=ACCENT2,
                     bg=SURFACE, width=3).pack(side="left")
            lbl = tk.Label(row, text="", font=FONT_INPUT,
                           fg=TEXT, bg=SURFACE, anchor="w", wraplength=480)
            lbl.pack(side="left", fill="x", expand=True)
            self.detail_fields[field] = lbl

        btn_row = tk.Frame(inner, bg=SURFACE)
        btn_row.pack(fill="x", anchor="w", pady=(20, 0))

        self._btn(btn_row, "✎  Edit Contact", self._start_edit,
                  bg=SURFACE2, fg=ACCENT).pack(side="left", padx=(0, 10))
        self._btn(btn_row, "✕  Delete", self._delete_contact,
                  bg=SURFACE2, fg=DANGER).pack(side="left")

        # empty-state (shown when nothing selected)
        self.empty_label = tk.Label(
            parent,
            text="◈\n\nSelect a contact\nto view details\n\nor open a JSON file\nto get started",
            font=("Georgia", 13), fg=TEXT_DIM, bg=BG,
            justify="center", pady=30
        )
        self.empty_label.pack(expand=True)

        # action buttons row (always visible at bottom of right pane)
        action_row = tk.Frame(parent, bg=BG, pady=16)
        action_row.pack(side="bottom", fill="x")

        self._btn(action_row, "+  Add New Contact", self._show_add_form,
                  bg=ACCENT, fg=TEXT_TITLE, padx=22, pady=9).pack(side="right")

        self._btn(action_row, "⟳  New File", self._new_file,
                  bg=SURFACE2, fg=TEXT_DIM, padx=14, pady=9).pack(side="right", padx=(0, 10))

    # ─── Add / Edit form pane ─────────────────
    def _build_form_pane(self, parent):
        self.form_frame = tk.Frame(parent, bg=BG)

        inner = tk.Frame(self.form_frame, bg=SURFACE, padx=30, pady=26)
        tk.Frame(inner, bg=ACCENT2, height=3).pack(fill="x")
        inner.pack(fill="both", expand=True, padx=28, pady=24)

        self.form_title_lbl = tk.Label(
            inner, text="ADD CONTACT",
            font=FONT_HEAD, fg=ACCENT2, bg=SURFACE, anchor="w"
        )
        self.form_title_lbl.pack(fill="x", pady=(14, 18))

        self.form_vars = {}
        for field, placeholder in [
            ("name",    "Full Name"),
            ("phone",   "Digits only"),
            ("address", "Street, City, Zip"),
            ("email",   "user@example.com"),
        ]:
            grp = tk.Frame(inner, bg=SURFACE)
            grp.pack(fill="x", pady=7)
            tk.Label(grp, text=field.upper(), font=FONT_LABEL,
                     fg=TEXT_DIM, bg=SURFACE).pack(anchor="w")
            var = tk.StringVar()
            self.form_vars[field] = var
            entry = tk.Entry(
                grp, textvariable=var,
                font=FONT_INPUT, bg=SURFACE2, fg=TEXT,
                insertbackground=TEXT, relief="flat", bd=0,
                highlightthickness=1, highlightbackground=BORDER,
                highlightcolor=ACCENT
            )
            entry.pack(fill="x", ipady=8, ipadx=8, pady=(4, 0))

        self.form_error = tk.Label(
            inner, text="", font=FONT_SMALL,
            fg=DANGER, bg=SURFACE, anchor="w"
        )
        self.form_error.pack(fill="x", pady=(6, 0))

        btn_row = tk.Frame(inner, bg=SURFACE, pady=12)
        btn_row.pack(fill="x")
        self._btn(btn_row, "✔  Save", self._save_form,
                  bg=ACCENT, fg=TEXT_TITLE, padx=20).pack(side="left")
        self._btn(btn_row, "Cancel", self._hide_form,
                  bg=SURFACE2, fg=TEXT_DIM).pack(side="left", padx=(10, 0))

    # ──────────────────────────────────────────
    # REUSABLE BUTTON HELPER
    # ──────────────────────────────────────────

    def _btn(self, parent, text, command, bg=SURFACE2,
             fg=TEXT, padx=14, pady=7, **kw):
        b = tk.Button(
            parent, text=text, command=command,
            font=FONT_BTN, bg=bg, fg=fg, activebackground=ACCENT,
            activeforeground=TEXT_TITLE, relief="flat", bd=0,
            padx=padx, pady=pady, cursor="hand2",
            **kw
        )
        # subtle hover
        b.bind("<Enter>", lambda e: b.config(bg=self._lighten(bg)))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    @staticmethod
    def _lighten(hex_color):
        """Lighten a hex colour slightly for hover effect."""
        try:
            r = min(255, int(hex_color[1:3], 16) + 20)
            g = min(255, int(hex_color[3:5], 16) + 20)
            b = min(255, int(hex_color[5:7], 16) + 20)
            return f"#{r:02X}{g:02X}{b:02X}"
        except Exception:
            return hex_color

    # ──────────────────────────────────────────
    # FILE OPERATIONS
    # ──────────────────────────────────────────

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Open Contact List",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                messagebox.showerror("Invalid File",
                    "The selected file does not contain a valid contact list (expected a JSON array).")
                return
            self.contacts      = data
            self.contacts_file = path
            self.file_label.config(
                text=f"📄 {os.path.basename(path)}",
                fg=ACCENT2
            )
            self.search_var.set("")
            self._refresh_list()
        except (json.JSONDecodeError, OSError) as e:
            messagebox.showerror("Error Opening File", str(e))

    def _new_file(self):
        path = filedialog.asksaveasfilename(
            title="Create New Contact File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if not path:
            return
        self.contacts      = []
        self.contacts_file = path
        self._save_to_disk()
        self.file_label.config(
            text=f"📄 {os.path.basename(path)}",
            fg=ACCENT2
        )
        self.search_var.set("")
        self._refresh_list()

    def _save_to_disk(self):
        if not self.contacts_file:
            path = filedialog.asksaveasfilename(
                title="Save Contact List As",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )
            if not path:
                return False
            self.contacts_file = path
            self.file_label.config(
                text=f"📄 {os.path.basename(path)}",
                fg=ACCENT2
            )
        try:
            with open(self.contacts_file, "w", encoding="utf-8") as f:
                json.dump(self.contacts, f, indent=4)
            return True
        except OSError as e:
            messagebox.showerror("Save Error", str(e))
            return False

    # ──────────────────────────────────────────
    # LIST MANAGEMENT
    # ──────────────────────────────────────────

    def _refresh_list(self, query=""):
        query = query.lower().strip()
        if query:
            self.filtered = [c for c in self.contacts if query in c.get("name", "").lower()]
        else:
            self.filtered = list(self.contacts)

        self.listbox.delete(0, "end")
        for contact in self.filtered:
            self.listbox.insert("end", f"  {contact.get('name', '(unnamed)')}")

        count = len(self.filtered)
        total = len(self.contacts)
        if query:
            self.count_label.config(text=f"{count} of {total} match")
        else:
            self.count_label.config(text=f"{total} contact{'s' if total != 1 else ''}")

        self._show_empty_state()

    def _do_search(self):
        self._refresh_list(self.search_var.get())
        self.selected_index = None
        self._show_empty_state()

    def _on_select(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        self.selected_index = sel[0]
        contact = self.filtered[self.selected_index]
        self._show_detail(contact)

    # ──────────────────────────────────────────
    # DETAIL VIEW
    # ──────────────────────────────────────────

    def _show_detail(self, contact):
        self._hide_form()
        self.empty_label.pack_forget()
        self.detail_card.pack(fill="both", expand=True)

        self.detail_name.config(text=contact.get("name", ""))
        self.detail_fields["phone"].config(text=contact.get("phone", "—"))
        self.detail_fields["address"].config(text=contact.get("address", "—"))
        self.detail_fields["email"].config(text=contact.get("email", "—"))

    def _show_empty_state(self):
        self._hide_form()
        self.detail_card.pack_forget()
        self.empty_label.pack(expand=True)
        self.selected_index = None

    # ──────────────────────────────────────────
    # ADD / EDIT FORM
    # ──────────────────────────────────────────

    def _show_add_form(self):
        if not self.contacts_file:
            messagebox.showinfo("No File Open",
                "Please open or create a JSON file first before adding contacts.")
            return
        self._editing_contact = None
        self.form_title_lbl.config(text="ADD CONTACT")
        for v in self.form_vars.values():
            v.set("")
        self.form_error.config(text="")
        self.detail_frame.pack_forget()
        self.form_frame.pack(fill="both", expand=True)

    def _start_edit(self):
        if self.selected_index is None:
            return
        contact = self.filtered[self.selected_index]
        self._editing_contact = contact
        self.form_title_lbl.config(text="EDIT CONTACT")
        for field, var in self.form_vars.items():
            var.set(contact.get(field, ""))
        self.form_error.config(text="")
        self.detail_frame.pack_forget()
        self.form_frame.pack(fill="both", expand=True)

    def _hide_form(self):
        self.form_frame.pack_forget()
        self.detail_frame.pack(fill="both", expand=True, padx=28, pady=24)

    def _save_form(self):
        name    = self.form_vars["name"].get().strip()
        phone   = self.form_vars["phone"].get().strip()
        address = self.form_vars["address"].get().strip()
        email   = self.form_vars["email"].get().strip()

        # Validate
        if not name:
            self.form_error.config(text="⚠  Name cannot be empty.")
            return
        if not is_valid_name(name):
            self.form_error.config(text="⚠  Name: letters and spaces only.")
            return
        if not phone:
            self.form_error.config(text="⚠  Phone cannot be empty.")
            return
        if not is_valid_phone(phone):
            self.form_error.config(text="⚠  Phone: digits only (no dashes or spaces).")
            return
        if not address:
            self.form_error.config(text="⚠  Address cannot be empty.")
            return
        if not email:
            self.form_error.config(text="⚠  Email cannot be empty.")
            return
        if not is_valid_email(email):
            self.form_error.config(text="⚠  Please enter a valid email (user@example.com).")
            return

        self.form_error.config(text="")

        if self._editing_contact is not None:
            # Edit existing contact in-place
            idx = self.contacts.index(self._editing_contact)
            self.contacts[idx] = {
                "name": name, "phone": phone,
                "address": address, "email": email
            }
        else:
            # Add new contact
            self.contacts.append({
                "name": name, "phone": phone,
                "address": address, "email": email
            })

        if not self._save_to_disk():
            return

        self._hide_form()
        self._refresh_list(self.search_var.get())

        # Re-select the contact we just saved
        new_contact = {"name": name, "phone": phone,
                       "address": address, "email": email}
        for i, c in enumerate(self.filtered):
            if c.get("name") == name and c.get("phone") == phone:
                self.listbox.selection_clear(0, "end")
                self.listbox.selection_set(i)
                self.listbox.see(i)
                self.selected_index = i
                self._show_detail(c)
                break

    # ──────────────────────────────────────────
    # DELETE
    # ──────────────────────────────────────────

    def _delete_contact(self):
        if self.selected_index is None:
            return
        contact = self.filtered[self.selected_index]
        name = contact.get("name", "this contact")
        if not messagebox.askyesno("Confirm Delete",
                f"Permanently delete '{name}'?\nThis cannot be undone."):
            return
        self.contacts.remove(contact)
        self._save_to_disk()
        self.selected_index = None
        self._refresh_list(self.search_var.get())
        self._show_empty_state()


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.tk_setPalette(background=BG, foreground=TEXT)

    # Try to set a nicer window icon (safe to fail silently)
    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    app = ContactBookApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

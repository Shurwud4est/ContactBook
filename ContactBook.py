"""
contact_book.py
---------------
A console-based Contact Book application that allows users to add, view,
search, and delete contacts. All data is saved to a JSON file so that
contacts persist even after the program closes.

Requirements: Python 3.x (no third-party libraries needed)
"""

import json   # Used to read and write data in JSON format
import os     # Used to check if the contacts file already exists
import re     # Used for "regular expressions" — pattern matching on strings


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

# The name of the file where contacts will be saved.
# Using a constant makes it easy to change the filename in one place.
CONTACTS_FILE = "contacts.json"


# ─────────────────────────────────────────────
# FILE I/O  (Input / Output)
# ─────────────────────────────────────────────

def load_contacts():
    """
    Load contacts from the JSON file and return them as a Python list.

    If the file does not exist yet (first run), return an empty list
    so the rest of the program can treat the data the same way.
    """
    # os.path.exists() returns True if the file is present on disk
    if os.path.exists(CONTACTS_FILE):
        # Open the file in read mode ("r") using UTF-8 encoding
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            # json.load() converts the JSON text in the file into
            # a native Python object (here, a list of dictionaries)
            return json.load(f)
    # File doesn't exist yet — start with an empty contact list
    return []


def save_contacts(contacts):
    """
    Save the current list of contacts to the JSON file, overwriting
    whatever was there before.

    Parameters
    ----------
    contacts : list
        The full list of contact dictionaries to persist.
    """
    # Open the file in write mode ("w"), which creates it if absent
    # or clears it if it already exists
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        # json.dump() converts the Python list into formatted JSON text.
        # indent=4 makes the file human-readable (pretty-printed).
        json.dump(contacts, f, indent=4)


# ─────────────────────────────────────────────
# VALIDATION HELPERS
# ─────────────────────────────────────────────

def is_valid_name(name):
    """
    Return True if the name contains only letters and spaces.

    A name like "John Smith" is valid; "J0hn" or "123" are not.
    re.fullmatch() checks that the ENTIRE string matches the pattern.
    The pattern [A-Za-z ]+ means: one or more letters (upper or lower)
    or space characters.
    """
    return bool(re.fullmatch(r"[A-Za-z ]+", name))


def is_valid_phone(phone):
    """
    Return True if the phone number contains only digits.

    Accepts any length of digits (e.g. "5551234567").
    Re-uses re.fullmatch() with pattern \d+ which means
    "one or more digit characters (0-9)".
    """
    return bool(re.fullmatch(r"\d+", phone))


def is_valid_email(email):
    """
    Return True if the email address looks valid.

    This uses a simplified pattern that requires:
      - one or more non-@ characters  (the local part)
      - the @ symbol
      - one or more non-@ characters  (the domain name)
      - a dot
      - two to four letters           (the top-level domain, e.g. com)

    Example valid:   alice@example.com
    Example invalid: alice@           or   aliceexample.com
    """
    pattern = r"[^@]+@[^@]+\.[A-Za-z]{2,4}"
    return bool(re.fullmatch(pattern, email))


# ─────────────────────────────────────────────
# CORE FEATURES
# ─────────────────────────────────────────────

def add_contact(contacts):
    """
    Interactively prompt the user for contact details, validate each
    field, and append a new contact dictionary to the contacts list.
    The updated list is immediately saved to disk.

    Parameters
    ----------
    contacts : list
        The in-memory list of contacts (modified in place).
    """
    print("\n--- Add New Contact ---")

    # ── Name ──────────────────────────────────
    # Keep asking until the user provides a valid name
    while True:
        name = input("Name: ").strip()          # .strip() removes leading/trailing whitespace
        if not name:
            print("  ⚠  Name cannot be empty.")
        elif not is_valid_name(name):
            print("  ⚠  Name must contain letters and spaces only (no numbers or symbols).")
        else:
            break   # Input is valid; exit the loop

    # ── Phone ─────────────────────────────────
    while True:
        phone = input("Phone (digits only): ").strip()
        if not phone:
            print("  ⚠  Phone number cannot be empty.")
        elif not is_valid_phone(phone):
            print("  ⚠  Phone must contain digits only (no spaces, dashes, or letters).")
        else:
            break

    # ── Address ───────────────────────────────
    # Address has no strict format requirement — just can't be blank
    while True:
        address = input("Address: ").strip()
        if not address:
            print("  ⚠  Address cannot be empty.")
        else:
            break

    # ── Email ─────────────────────────────────
    while True:
        email = input("Email: ").strip()
        if not email:
            print("  ⚠  Email cannot be empty.")
        elif not is_valid_email(email):
            print("  ⚠  Please enter a valid email address (e.g. user@example.com).")
        else:
            break

    # Build a dictionary that represents one contact
    new_contact = {
        "name":    name,
        "phone":   phone,
        "address": address,
        "email":   email
    }

    # Add the new contact to the in-memory list
    contacts.append(new_contact)

    # Immediately write the updated list to disk so data is not lost
    save_contacts(contacts)

    print(f"\n  ✔  Contact '{name}' saved successfully!")


def view_contacts(contacts):
    """
    Print all contacts in a numbered, readable format.

    Parameters
    ----------
    contacts : list
        The in-memory list of contacts.
    """
    print("\n--- All Contacts ---")

    # Handle the case where no contacts have been added yet
    if not contacts:
        print("  (No contacts found. Add one first!)")
        return

    # enumerate() gives both the index and the value while looping.
    # We start counting at 1 (start=1) instead of 0 for user-friendliness.
    for i, contact in enumerate(contacts, start=1):
        print(f"\n  [{i}] {contact['name']}")
        print(f"      Phone:   {contact['phone']}")
        print(f"      Address: {contact['address']}")
        print(f"      Email:   {contact['email']}")


def search_contact(contacts):
    """
    Search for contacts whose name contains the user-provided query
    (case-insensitive) and display any matches.

    Parameters
    ----------
    contacts : list
        The in-memory list of contacts.
    """
    print("\n--- Search Contacts ---")
    query = input("Enter name to search: ").strip().lower()  # .lower() for case-insensitive matching

    if not query:
        print("  ⚠  Search term cannot be empty.")
        return

    # List comprehension: build a new list that contains only contacts
    # whose name (converted to lowercase) includes the search query.
    results = [c for c in contacts if query in c["name"].lower()]

    if not results:
        print(f"  No contacts found matching '{query}'.")
    else:
        print(f"\n  Found {len(results)} match(es):")
        for contact in results:
            print(f"\n    Name:    {contact['name']}")
            print(f"    Phone:   {contact['phone']}")
            print(f"    Address: {contact['address']}")
            print(f"    Email:   {contact['email']}")


def delete_contact(contacts):
    """
    Search for a contact by name and, after user confirmation, remove it
    from the list. Saves the updated list to disk.

    Parameters
    ----------
    contacts : list
        The in-memory list of contacts (modified in place).
    """
    print("\n--- Delete Contact ---")
    query = input("Enter the name of the contact to delete: ").strip().lower()

    if not query:
        print("  ⚠  Name cannot be empty.")
        return

    # Find all contacts whose name contains the search query
    matches = [c for c in contacts if query in c["name"].lower()]

    if not matches:
        print(f"  No contacts found matching '{query}'.")
        return

    # If more than one match is found, show them all so the user
    # can identify exactly which contact to remove
    if len(matches) > 1:
        print(f"\n  Multiple matches found:")
        for i, contact in enumerate(matches, start=1):
            print(f"    [{i}] {contact['name']}  |  {contact['phone']}")
        # Ask the user to pick one by number
        try:
            choice = int(input("  Enter the number of the contact to delete: "))
            if choice < 1 or choice > len(matches):
                print("  ⚠  Invalid selection.")
                return
            # Adjust from 1-based user input to 0-based list index
            target = matches[choice - 1]
        except ValueError:
            # int() will raise ValueError if the user types something non-numeric
            print("  ⚠  Please enter a number.")
            return
    else:
        # Only one match — use it directly
        target = matches[0]

    # Confirm before deleting to prevent accidental removal
    confirm = input(f"\n  Are you sure you want to delete '{target['name']}'? (yes/no): ").strip().lower()

    if confirm in ("yes", "y"):
        contacts.remove(target)    # Remove the matching dictionary from the list
        save_contacts(contacts)    # Persist the change immediately
        print(f"  ✔  Contact '{target['name']}' deleted.")
    else:
        print("  Deletion cancelled.")


# ─────────────────────────────────────────────
# MENU & MAIN ENTRY POINT
# ─────────────────────────────────────────────

def display_menu():
    """
    Print the main menu options to the console.
    Kept in its own function so the menu text is defined in one place.
    """
    print("\n╔══════════════════════════════╗")
    print("║       CONTACT BOOK           ║")
    print("╠══════════════════════════════╣")
    print("║  1. Add Contact              ║")
    print("║  2. View All Contacts        ║")
    print("║  3. Search Contact           ║")
    print("║  4. Delete Contact           ║")
    print("║  5. Exit                     ║")
    print("╚══════════════════════════════╝")


def main():
    """
    Main program loop.

    Loads existing contacts from disk, then repeatedly shows the menu
    and routes the user's choice to the appropriate function until
    they choose to exit.
    """
    # Load any previously saved contacts from the JSON file
    contacts = load_contacts()

    print("Welcome to your Contact Book!")

    # Loop forever until the user explicitly chooses to exit (option 5)
    while True:
        display_menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_contact(contacts)
        elif choice == "2":
            view_contacts(contacts)
        elif choice == "3":
            search_contact(contacts)
        elif choice == "4":
            delete_contact(contacts)
        elif choice == "5":
            print("\nGoodbye! Your contacts are saved.\n")
            break   # Exit the while loop, ending the program
        else:
            # The user typed something other than 1–5
            print("  ⚠  Invalid option. Please enter a number between 1 and 5.")


# ─────────────────────────────────────────────
# SCRIPT GUARD
# ─────────────────────────────────────────────

# This block ensures main() is only called when this file is run directly.
# If another Python file were to import this one, main() would NOT
# automatically execute — which is considered best practice.
if __name__ == "__main__":
    main()
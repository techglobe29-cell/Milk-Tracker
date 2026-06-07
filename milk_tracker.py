import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk


# ==================== DATABASE FUNCTIONS ====================
def init_db():
    """Initializes the SQLite database and creates the table if it doesn't exist."""
    conn = sqlite3.connect("milk_tracker.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS milk_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            quantity REAL NOT NULL,
            price_per_liter REAL NOT NULL,
            total_cost REAL NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


def insert_record(date, quantity, price):
    """Inserts a new milk record into the database."""
    total_cost = quantity * price
    conn = sqlite3.connect("milk_tracker.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO milk_records (date, quantity, price_per_liter, total_cost)
        VALUES (?, ?, ?, ?)
    """,
        (date, quantity, price, total_cost),
    )
    conn.commit()
    conn.close()


def fetch_all_records():
    """Fetches all records from the database, sorted by date descending."""
    conn = sqlite3.connect("milk_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM milk_records ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


# ==================== GUI APPLICATION class ====================
class MilkTrackerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("🍼 Milk Tracking & Expenses App")
        self.root.geometry("650x500")
        self.root.config(bg="#f4f6f9")

        # Title Label
        title = tk.Label(
            root,
            text="Daily Milk Tracker",
            font=("Arial", 18, "bold"),
            bg="#f4f6f9",
            fg="#2c3e50",
        )
        title.pack(pady=10)

        # ---------------- INPUT FRAME ----------------
        input_frame = tk.LabelFrame(
            root,
            text=" Add New Record ",
            font=("Arial", 10, "bold"),
            bg="#f4f6f9",
            padx=10,
            pady=10,
        )
        input_frame.pack(pady=10, fill="x", padx=20)

        # Date Input
        tk.Label(input_frame, text="Date (YYYY-MM-DD):", bg="#f4f6f9").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.ent_date = tk.Entry(input_frame)
        self.ent_date.insert(
            0, datetime.now().strftime("%Y-%m-%d")
        )  # Pre-fill today's date
        self.ent_date.grid(row=0, column=1, padx=5, pady=5)

        # Quantity Input
        tk.Label(input_frame, text="Quantity (Liters):", bg="#f4f6f9").grid(
            row=0, column=2, sticky="w", padx=5, pady=5
        )
        self.ent_qty = tk.Entry(input_frame)
        self.ent_qty.grid(row=0, column=3, padx=5, pady=5)

        # Price Input
        tk.Label(input_frame, text="Price per Liter ($):", bg="#f4f6f9").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.ent_price = tk.Entry(input_frame)
        self.ent_price.insert(0, "1.50")  # Default price placeholder
        self.ent_price.grid(row=1, column=1, padx=5, pady=5)

        # Submit Button
        btn_submit = tk.Button(
            input_frame,
            text="Save Record",
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.add_record,
        )
        btn_submit.grid(row=1, column=3, columnspan=2, sticky="e", padx=5)

        # ---------------- DATA VIEW FRAME ----------------
        view_frame = tk.Frame(root, bg="#f4f6f9")
        view_frame.pack(pady=10, fill="both", expand=True, padx=20)

        # Treeview (Table) to show SQL data
        columns = ("id", "date", "qty", "price", "total")
        self.tree = ttk.Treeview(
            view_frame, columns=columns, show="headings", height=10
        )

        # Define headings
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("qty", text="Quantity (L)")
        self.tree.heading("price", text="Price/L ($)")
        self.tree.heading("total", text="Total Cost ($)")

        # Define column widths
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("qty", width=100, anchor="center")
        self.tree.column("price", width=100, anchor="center")
        self.tree.column("total", width=120, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar for Table
        scrollbar = ttk.Scrollbar(
            view_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Load initial data from SQLite
        self.view_records()

    # ==================== APP LOGIC ====================
    def add_record(self):
        """Validates inputs, saves to SQLite, and refreshes the table."""
        date = self.ent_date.get().strip()
        qty_str = self.ent_qty.get().strip()
        price_str = self.ent_price.get().strip()

        # Basic Validation
        if not date or not qty_str or not price_str:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            quantity = float(qty_str)
            price = float(price_str)
            # Verify date format
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Error",
                "Invalid inputs! Ensure numbers are numeric and date format is YYYY-MM-DD.",
            )
            return

        # Save to DB
        insert_record(date, quantity, price)
        messagebox.showinfo("Success", "Record saved successfully!")

        # Clear inputs & Refresh view
        self.ent_qty.delete(0, tk.END)
        self.view_records()

    def view_records(self):
        """Clears the current table grid and pulls fresh data from SQLite."""
        # Clear existing rows in UI
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Grab rows from database
        records = fetch_all_records()
        for row in records:
            # format values nicely
            formatted_row = (
                row[0],
                row[1],
                f"{row[2]:.2f}",
                f"${row[3]:.2f}",
                f"${row[4]:.2f}",
            )
            self.tree.insert("", tk.END, values=formatted_row)


# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    init_db()  # Make sure database is ready
    root = tk.Tk()
    app = MilkTrackerApp(root)
    root.mainloop()
import sqlite3
from datetime import datetime
import streamlit as st

# Initialize SQLite database
conn = sqlite3.connect("milk_tracker.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS milk_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT, quantity REAL, price REAL, total REAL
    )
"""
)
conn.commit()

st.title("🍼 Milk Tracking App")

# Input form
with st.form("milk_form", clear_on_submit=True):
    date = st.date_input("Select Date", datetime.now())
    qty = st.number_input("Quantity (Liters)", min_value=0.0, step=0.5)
    price = st.number_input("Price per Liter ($)", min_value=0.0, value=1.50)
    submit = st.form_submit_button("Save Record")

    if submit and qty > 0:
        total = qty * price
        cursor.execute(
            "INSERT INTO milk_records (date, quantity, price, total) VALUES (?, ?, ?, ?)",
            (str(date), qty, price, total),
        )
        conn.commit()
        st.success("Record saved!")

# Display Data Table
st.subheader("📋 Past Records")
cursor.execute("SELECT date, quantity, price, total FROM milk_records ORDER BY date DESC")
data = cursor.fetchall()

if data:
    st.table(
        [
            {"Date": r[0], "Qty (L)": r[1], "Price/L": f"${r[2]:.2f}", "Total": f"${r[3]:.2f}"}
            for r in data
        ]
    )
else:
    st.info("No records found yet.")

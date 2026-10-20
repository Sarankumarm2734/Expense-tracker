
from flask import Flask, render_template, request
import sqlite3
from pathlib import Path

app = Flask(__name__)

# Store the database in the same folder as app.py
DB_PATH = Path(__file__).parent / "ExpenseTracker.db"


def create_table():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                sno INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                expense_date TEXT DEFAULT CURRENT_DATE
            )
        """)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    category = request.form.get("category", "").strip()
    amount_text = request.form.get("amount", "").strip()
    description = request.form.get("description", "").strip()

    # Validate the user's input
    if not category or not amount_text:
        return render_template(
            "index.html",
            error="Please enter a category and amount."
        )

    try:
        amount = float(amount_text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        return render_template(
            "index.html",
            error="Please enter a valid amount greater than zero."
        )

    # Save the expense in SQLite
    with sqlite3.connect(DB_PATH) as con:
        cursor = con.execute("""
            INSERT INTO expenses (category, amount, description)
            VALUES (?, ?, ?)
        """, (category, amount, description))

        expense_id = cursor.lastrowid

        cursor.execute("""
            SELECT sno, category, amount, description, expense_date
            FROM expenses
            WHERE sno = ?
        """, (expense_id,))

        expense = cursor.fetchone()

    # Display the saved expense in the VS Code terminal
    print("\n========== NEW EXPENSE SAVED ==========", flush=True)
    print(f"ID          : {expense[0]}", flush=True)
    print(f"Category    : {expense[1]}", flush=True)
    print(f"Amount      : ₹{expense[2]:.2f}", flush=True)
    print(f"Description : {expense[3] or '-'}", flush=True)
    print(f"Date        : {expense[4]}", flush=True)
    print("=======================================\n", flush=True)

    # Display the form again, with empty input fields
    return render_template(
        "index.html",
        message="Expense saved successfully! You can enter another expense."
    )


if __name__ == "__main__":
    create_table()
    print(f"Database location: {DB_PATH}", flush=True)
    app.run(debug=True)

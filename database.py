import sqlite3
import os
import pandas as pd
DB_PATH = "data/expenses.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        date TEXT,
        amount REAL,
        merchant TEXT,
        category TEXT,
        subject TEXT,
        body_preview TEXT
    )
    """)

    conn.commit()
    conn.close()


# ensures no duplicate entry goes into the database.

def insert_transactions(user_email, transactions):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    new_inserted = 0
    for txn in transactions:
        # Check for duplicate
        cursor.execute("""
            SELECT COUNT(*) FROM transactions
            WHERE user_email = ? AND date = ? AND amount = ? AND merchant = ?
        """, (user_email, txn["Date"], txn["Amount"], txn["Merchant"]))

        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO transactions (user_email, date, amount, merchant, category, subject, body_preview)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_email,
                txn["Date"],
                txn["Amount"],
                txn["Merchant"],
                txn["Category"],
                txn["Subject"],
                txn["Body_Preview"]
            ))
            new_inserted += 1

    conn.commit()
    conn.close()
    return new_inserted


#Fetch Transactions from DB by Date Range

def fetch_transactions_db(user_email, start_date, end_date):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, amount, merchant, category, subject, body_preview
        FROM transactions
        WHERE user_email = ?
        AND date BETWEEN ? AND ?
        ORDER BY date ASC
    """, (user_email, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))

    rows = cursor.fetchall()
    conn.close()

    columns = ["Date", "Amount", "Merchant", "Category", "Subject", "Body_Preview"]
    df = pd.DataFrame(rows, columns=columns)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    return df


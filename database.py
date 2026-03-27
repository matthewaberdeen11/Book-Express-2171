#datbase template 

"""
database.py - Database initialization and connection management.
Handles SQLite setup, table creation, and sample data seeding.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "book_express.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory_item (
            item_id TEXT PRIMARY KEY,
            item_name TEXT NOT NULL,
            unit_price REAL NOT NULL DEFAULT 0.0,
            stock_quantity INTEGER NOT NULL DEFAULT 0,
            reorder_threshold INTEGER NOT NULL DEFAULT 5,
            grade TEXT,
            subject TEXT,
            availability_status TEXT DEFAULT 'In Stock'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS import_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            filename TEXT NOT NULL,
            user_id TEXT NOT NULL,
            total_sales_amount REAL DEFAULT 0.0,
            records_processed INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS low_stock_alert (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT NOT NULL,
            current_quantity INTEGER NOT NULL,
            threshold INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (item_id) REFERENCES inventory_item(item_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT
        )
    """)

    # Seed sample data if empty
    c.execute("SELECT COUNT(*) FROM inventory_item")
    if c.fetchone()[0] == 0:
        sample = [
            ("BK001", "Mathematics for Grade 1", 1500.00, 50, 10, "Grade 1", "Mathematics"),
            ("BK002", "English Language Grade 1", 1200.00, 35, 8, "Grade 1", "English"),
            ("BK003", "Science Explorer Grade 2", 1800.00, 20, 10, "Grade 2", "Science"),
            ("BK004", "Social Studies Grade 3", 1400.00, 15, 5, "Grade 3", "Social Studies"),
            ("BK005", "Reading Comprehension Grade 2", 1100.00, 8, 10, "Grade 2", "English"),
            ("BK006", "Advanced Mathematics Grade 4", 2000.00, 40, 10, "Grade 4", "Mathematics"),
            ("BK007", "Art & Craft Supplies Kit", 900.00, 60, 15, "All", "Art"),
            ("BK008", "Geography Workbook Grade 5", 1600.00, 12, 5, "Grade 5", "Geography"),
            ("BK009", "Spanish Beginner Grade 3", 1300.00, 25, 8, "Grade 3", "Spanish"),
            ("BK010", "History of Jamaica Grade 6", 1750.00, 30, 10, "Grade 6", "History"),
        ]
        c.executemany(
            "INSERT INTO inventory_item (item_id, item_name, unit_price, stock_quantity, reorder_threshold, grade, subject) VALUES (?, ?, ?, ?, ?, ?, ?)",
            sample
        )
        print("Seeded 10 sample inventory items.")

    conn.commit()
    conn.close()
    print("Database initialized.")


if __name__ == "__main__":
    init_db()
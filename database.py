#datbase template 
"""
database.py - Database initialization and connection management.
Handles SQLite setup, table creation, and sample data seeding.
"""

import sqlite3
import os
import random

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "book_express.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def generate_inventory_items(
    record_count=50000,
    price_min=1000,
    price_max=5000,
    quantity_min=0,
    quantity_max=100,
    reorder_min=5,
    reorder_max=20,
):
    subjects = [
        "Mathematics", "English", "Science", "Social Studies", "History",
        "Geography", "Spanish", "French", "Biology", "Chemistry",
        "Physics", "Accounting", "Economics", "Information Technology",
        "Religious Education", "Art", "Music", "Literature", "Language Arts",
        "Integrated Science", "Computer Science", "Business Studies"
    ]

    prefixes = [
        "Introduction to", "Fundamentals of", "Essentials of", "Principles of",
        "Advanced", "Applied", "Practical", "Modern", "Complete", "Interactive",
        "Illustrated", "Comprehensive", "Core", "Mastering", "Understanding"
    ]

    middles = [
        "for", "in", "of", "through", "with", "and", "Workbook for",
        "Guide to", "Studies in", "Skills in", "Activities in"
    ]

    levels = [
        "Beginners", "Intermediate Learners", "Advanced Learners",
        "Primary Level", "Secondary Level", "Junior Students",
        "Senior Students", "Examination Prep", "Student Workbook",
        "Practice Manual", "Revision Course", "Foundations", "Mastery Level"
    ]

    editions = [
        "1st Edition", "2nd Edition", "3rd Edition", "Revised Edition",
        "Updated Edition", "Student Edition", "School Edition", "Teacher Edition"
    ]

    tags = [
        "Workbook", "Textbook", "Practice Book", "Study Guide",
        "Revision Book", "Activity Book", "Companion", "Handbook"
    ]

    connectors = ["of", "for", "in", "with", "through", "and"]

    records = []

    for i in range(1, record_count + 1):
        subject = random.choice(subjects)
        grade_num = random.randint(1, 13)
        grade = f"Grade {grade_num}"

        # Price in steps of 50
        price = random.randrange(price_min, price_max + 50, 50)

        quantity = random.randint(quantity_min, quantity_max)
        reorder_threshold = random.randint(reorder_min, reorder_max)

        # Build a more varied item name
        pattern = random.randint(1, 6)

        if pattern == 1:
            item_name = f"{random.choice(prefixes)} {subject} {random.choice(middles)} {grade}"
        elif pattern == 2:
            item_name = f"{subject} {random.choice(tags)} {random.choice(connectors)} {grade}"
        elif pattern == 3:
            item_name = f"{random.choice(prefixes)} {subject}: {random.choice(levels)} for {grade}"
        elif pattern == 4:
            item_name = f"{subject} {random.choice(tags)} - {random.choice(editions)}"
        elif pattern == 5:
            item_name = f"{random.choice(prefixes)} {subject} {random.choice(connectors)} {random.choice(levels)}"
        else:
            item_name = f"{subject} for {grade} - {random.choice(tags)} ({random.choice(editions)})"

        item_id = f"BK{i:05d}"

        availability_status = "In Stock" if quantity > 0 else "Out of Stock"

        records.append((
            item_id,
            item_name,
            price,
            quantity,
            reorder_threshold,
            grade,
            subject,
            availability_status
        ))

    return records


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

    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory_adjustment (
            adjustment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT NOT NULL,
            type TEXT NOT NULL,
            quantity_changed INTEGER NOT NULL,
            message TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES inventory_item(item_id)
            )
    """)

    # Seed sample data if empty
    c.execute("SELECT COUNT(*) FROM inventory_item")
    if c.fetchone()[0] == 0:
        RECORD_COUNT = 50000

        PRICE_MIN = 1000
        PRICE_MAX = 5000

        QUANTITY_MIN = 30
        QUANTITY_MAX = 200

        REORDER_MIN = 5
        REORDER_MAX = 25

        sample = generate_inventory_items(
            record_count=RECORD_COUNT,
            price_min=PRICE_MIN,
            price_max=PRICE_MAX,
            quantity_min=QUANTITY_MIN,
            quantity_max=QUANTITY_MAX,
            reorder_min=REORDER_MIN,
            reorder_max=REORDER_MAX
        )

        c.executemany(
            """
            INSERT INTO inventory_item
            (item_id, item_name, unit_price, stock_quantity, reorder_threshold, grade, subject, availability_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            sample
        )

        print(f"Seeded {RECORD_COUNT} inventory items.")

    conn.commit()
    conn.close()
    print("Database initialized.")


if __name__ == "__main__":
    init_db()
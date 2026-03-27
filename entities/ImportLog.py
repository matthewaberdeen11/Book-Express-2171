"""
ImportLog <<Entity>>
Records each CSV import activity for audit trail.
Maps to ImportLog on the class diagram.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from database import get_connection


class ImportLog:

    logs = []  # Class-level storage

    def __init__(self, log_id: int = None, timestamp: str = None,
                 filename: str = "", user_id: str = "",
                 total_sales_amount: float = 0.0,
                 records_processed: int = 0, error_count: int = 0):
        self.log_id = log_id
        self.timestamp = timestamp or datetime.now().isoformat()
        self.filename = filename
        self.user_id = user_id
        self.total_sales_amount = total_sales_amount
        self.records_processed = records_processed
        self.error_count = error_count

    def create_log(self) -> None:
        """Persist this log entry to the database."""
        conn = get_connection()
        cursor = conn.execute("""
            INSERT INTO import_log (timestamp, filename, user_id, total_sales_amount, records_processed, error_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.timestamp, self.filename, self.user_id,
              self.total_sales_amount, self.records_processed, self.error_count))
        self.log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        ImportLog.logs.append(self)

    def get_log_summary(self) -> str:
        return (f"Import Log #{self.log_id} | {self.timestamp}\n"
                f"  File: {self.filename} | User: {self.user_id}\n"
                f"  Records: {self.records_processed} | Errors: {self.error_count}\n"
                f"  Sales Total: ${self.total_sales_amount:,.2f}")

    @staticmethod
    def get_recent(limit: int = 10):
        conn = get_connection()
        rows = conn.execute("SELECT * FROM import_log ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [ImportLog(
            log_id=r["log_id"], timestamp=r["timestamp"], filename=r["filename"],
            user_id=r["user_id"], total_sales_amount=r["total_sales_amount"],
            records_processed=r["records_processed"], error_count=r["error_count"]
        ) for r in rows]

    def to_dict(self) -> dict:
        return {
            "log_id": self.log_id, "timestamp": self.timestamp,
            "filename": self.filename, "user_id": self.user_id,
            "total_sales_amount": self.total_sales_amount,
            "records_processed": self.records_processed, "error_count": self.error_count
        }

    def __repr__(self):
        return f"ImportLog(#{self.log_id}, processed={self.records_processed})"

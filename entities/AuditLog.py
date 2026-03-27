"""
AuditLog <<Entity>>
Records user actions for audit trail (UC-002).
Maps to AuditLog on the class diagram.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from database import get_connection


class AuditLog:

    logs = []  # Class-level storage

    def __init__(self, log_id: int = None, timestamp: str = None,
                 user_id: str = "", action: str = "", details: str = ""):
        self.log_id = log_id
        self.timestamp = timestamp or datetime.now().isoformat()
        self.user_id = user_id
        self.action = action
        self.details = details

    def create_entry(self) -> None:
        """Persist this audit entry to the database."""
        conn = get_connection()
        cursor = conn.execute("""
            INSERT INTO audit_log (timestamp, user_id, action, details)
            VALUES (?, ?, ?, ?)
        """, (self.timestamp, self.user_id, self.action, self.details))
        self.log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        AuditLog.logs.append(self)

    def get_log_summary(self) -> str:
        return f"Audit #{self.log_id} | {self.action} | {self.timestamp} | User: {self.user_id}"

    @staticmethod
    def get_recent(limit: int = 20):
        conn = get_connection()
        rows = conn.execute("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [AuditLog(
            log_id=r["log_id"], timestamp=r["timestamp"],
            user_id=r["user_id"], action=r["action"], details=r["details"]
        ) for r in rows]

    def to_dict(self) -> dict:
        return {
            "log_id": self.log_id, "timestamp": self.timestamp,
            "user_id": self.user_id, "action": self.action, "details": self.details
        }

    def __repr__(self):
        return f"AuditLog(#{self.log_id}, action='{self.action}')"

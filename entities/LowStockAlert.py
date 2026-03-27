"""
LowStockAlert <<Entity>>
Alert for items below reorder threshold.
Maps to LowStockAlert on the class diagram.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from database import get_connection


class LowStockAlert:

    def __init__(self, alert_id: int = None, item_id: str = "",
                 current_quantity: int = 0, threshold: int = 0,
                 created_at: str = None, status: str = "active"):
        self.alert_id = alert_id
        self.item_id = item_id
        self.current_quantity = current_quantity
        self.threshold = threshold
        self.created_at = created_at or datetime.now().isoformat()
        self.status = status

    def create_alert(self) -> None:
        """Persist alert to database."""
        conn = get_connection()
        cursor = conn.execute("""
            INSERT INTO low_stock_alert (item_id, current_quantity, threshold, created_at, status)
            VALUES (?, ?, ?, ?, ?)
        """, (self.item_id, self.current_quantity, self.threshold, self.created_at, self.status))
        self.alert_id = cursor.lastrowid
        conn.commit()
        conn.close()

    @staticmethod
    def is_duplicate(item_id: str) -> bool:
        """Check if active alert already exists for this item."""
        conn = get_connection()
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM low_stock_alert WHERE item_id = ? AND status = 'active'",
            (item_id,)
        ).fetchone()
        conn.close()
        return row["cnt"] > 0

    def resolve_alert(self) -> None:
        """Mark alert as resolved."""
        self.status = "resolved"
        conn = get_connection()
        conn.execute("UPDATE low_stock_alert SET status = 'resolved' WHERE alert_id = ?", (self.alert_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_active_alerts():
        conn = get_connection()
        rows = conn.execute("""
            SELECT a.*, i.item_name FROM low_stock_alert a
            JOIN inventory_item i ON a.item_id = i.item_id
            WHERE a.status = 'active' ORDER BY a.created_at DESC
        """).fetchall()
        conn.close()
        return [{
            "alert_id": r["alert_id"], "item_id": r["item_id"],
            "item_name": r["item_name"], "current_quantity": r["current_quantity"],
            "threshold": r["threshold"], "created_at": r["created_at"], "status": r["status"]
        } for r in rows]

    def to_dict(self) -> dict:
        return {
            "alert_id": self.alert_id, "item_id": self.item_id,
            "current_quantity": self.current_quantity, "threshold": self.threshold,
            "created_at": self.created_at, "status": self.status
        }

    def __repr__(self):
        return f"LowStockAlert(item={self.item_id}, qty={self.current_quantity}, status={self.status})"

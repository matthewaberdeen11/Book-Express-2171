"""
InventoryAdjustment <<Entity>>
Defines the InventoryAdjustment class for tracking inventory changes.
This class provides methods to create adjustment entries and retrieve recent adjustments for an item.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from database import get_connection

class InventoryAdjustment:

    adjustments = []  # Class-level storage for adjustments

    def __init__(self, adjustment_id: int = None, item_id: str = "",
                 type: str = "", quantity_changed: int = 0, message: str = "", timestamp: str = None):
        self.adjustment_id = adjustment_id
        self.item_id = item_id
        self.type = type
        self.quantity_changed = quantity_changed
        self.message = message
        self.timestamp = timestamp or datetime.now().isoformat()

    def create_entry(self) -> None:
        """Persist this adjustment entry to the database."""
        conn = get_connection()
        cursor = conn.execute("""
            INSERT INTO inventory_adjustment (item_id, type, quantity_changed, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (self.item_id, self.type, self.quantity_changed, self.message, self.timestamp))
        self.adjustment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        InventoryAdjustment.adjustments.append(self)

    @staticmethod
    def get_recent_for_item(item_id: str, limit: int = 10):
        conn = get_connection()
        rows = conn.execute("""
            SELECT * FROM inventory_adjustment
            WHERE item_id = ? ORDER BY timestamp DESC LIMIT ?
        """, (item_id, limit)).fetchall()
        conn.close()
        return [InventoryAdjustment(
            adjustment_id=r["adjustment_id"], item_id=r["item_id"],
            type=r["type"], quantity_changed=r["quantity_changed"],
            message=r["message"], timestamp=r["timestamp"]
        ) for r in rows]
    
    @staticmethod
    def get_recent_for_item_as_dicts(item_id: str, limit: int = 10):
        conn = get_connection()
        rows = conn.execute("""
            SELECT * FROM inventory_adjustment
            WHERE item_id = ? ORDER BY timestamp DESC LIMIT ?
        """, (item_id, limit)).fetchall()
        conn.close()
        return [{
            "adjustment_id": r["adjustment_id"], "item_id": r["item_id"],
            "type": r["type"], "quantity_changed": r["quantity_changed"],
            "message": r["message"], "timestamp": r["timestamp"]
        } for r in rows]

    def get_adjustment_summary(self) -> str:
        return (f"Adjustment #{self.adjustment_id} | Item: {self.item_id} | "
                f"Type: {self.type} | Qty Change: {self.quantity_changed} | "
                f"Time: {self.timestamp}\n  Message: {self.message}")
    
    def to_dict(self) -> dict:
        return {
            "adjustment_id": self.adjustment_id,
            "item_id": self.item_id,
            "type": self.type,
            "quantity_changed": self.quantity_changed,
            "message": self.message,
            "timestamp": self.timestamp
        }
"""
InventoryAdjustment <<Entity>>
Tracks manual inventory adjustments and price changes for catalogue items.

Supports:
- Manual stock adjustments with reason, notes, user identity, previous/new quantity, and timestamp
- Price change history with previous/new price, effective date, and user identity
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from database import get_connection


class InventoryAdjustment:

    VALID_REASONS = ["Damaged", "Customer Return", "Stock Correction", "Theft/Loss", "Other"]

    def __init__(
        self,
        adjustment_id: int = None,
        item_id: str = "",
        change_category: str = "",   # "stock_adjustment" or "price_change"
        user_id: str = "",
        reason: str = "",
        notes: str = "",
        previous_quantity: int = None,
        new_quantity: int = None,
        adjustment_amount: int = None,
        previous_price: float = None,
        new_price: float = None,
        effective_date: str = None,
        timestamp: str = None
    ):
        self.adjustment_id = adjustment_id
        self.item_id = item_id
        self.change_category = change_category
        self.user_id = user_id
        self.reason = reason
        self.notes = notes[:500] if notes else ""
        self.previous_quantity = previous_quantity
        self.new_quantity = new_quantity
        self.adjustment_amount = adjustment_amount
        self.previous_price = previous_price
        self.new_price = new_price
        self.effective_date = effective_date or datetime.now().isoformat()
        self.timestamp = timestamp or datetime.now().isoformat()

    def create_entry(self) -> None:
        """Persist this adjustment or price-change entry to the database."""
        self.validate()

        conn = get_connection()
        cursor = conn.execute("""
            INSERT INTO inventory_adjustment (
                item_id,
                change_category,
                user_id,
                reason,
                notes,
                previous_quantity,
                new_quantity,
                adjustment_amount,
                previous_price,
                new_price,
                effective_date,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.item_id,
            self.change_category,
            self.user_id,
            self.reason,
            self.notes,
            self.previous_quantity,
            self.new_quantity,
            self.adjustment_amount,
            self.previous_price,
            self.new_price,
            self.effective_date,
            self.timestamp
        ))
        self.adjustment_id = cursor.lastrowid
        conn.commit()
        conn.close()

    def validate(self) -> None:
        """Validate the entry before saving."""
        if not self.item_id:
            raise ValueError("item_id is required.")

        if not self.user_id:
            raise ValueError("user_id is required.")

        if self.change_category not in ["stock_adjustment", "price_change"]:
            raise ValueError("change_category must be 'stock_adjustment' or 'price_change'.")

        if self.notes and len(self.notes) > 500:
            raise ValueError("notes cannot exceed 500 characters.")

        if self.change_category == "stock_adjustment":
            if self.reason not in self.VALID_REASONS:
                raise ValueError(f"reason must be one of: {', '.join(self.VALID_REASONS)}")

            if self.previous_quantity is None or self.new_quantity is None:
                raise ValueError("previous_quantity and new_quantity are required for stock adjustments.")

            if self.adjustment_amount is None:
                self.adjustment_amount = self.new_quantity - self.previous_quantity

        if self.change_category == "price_change":
            if self.previous_price is None or self.new_price is None:
                raise ValueError("previous_price and new_price are required for price changes.")

    @staticmethod
    def create_stock_adjustment(
        item_id: str,
        user_id: str,
        previous_quantity: int,
        new_quantity: int,
        reason: str,
        notes: str = ""
    ):
        """Create and persist a manual inventory adjustment."""
        adjustment = InventoryAdjustment(
            item_id=item_id,
            change_category="stock_adjustment",
            user_id=user_id,
            reason=reason,
            notes=notes,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            adjustment_amount=new_quantity - previous_quantity
        )
        adjustment.create_entry()
        return adjustment

    @staticmethod
    def create_price_change(
        item_id: str,
        user_id: str,
        previous_price: float,
        new_price: float,
        notes: str = ""
    ):
        """Create and persist a price change history record."""
        adjustment = InventoryAdjustment(
            item_id=item_id,
            change_category="price_change",
            user_id=user_id,
            reason="Price Change",
            notes=notes,
            previous_price=previous_price,
            new_price=new_price
        )
        adjustment.create_entry()
        return adjustment

    @staticmethod
    def get_recent_for_item(item_id: str, limit: int = 10):
        conn = get_connection()
        rows = conn.execute("""
            SELECT * FROM inventory_adjustment
            WHERE item_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (item_id, limit)).fetchall()
        conn.close()

        return [
            InventoryAdjustment(
                adjustment_id=r["adjustment_id"],
                item_id=r["item_id"],
                change_category=r["change_category"],
                user_id=r["user_id"],
                reason=r["reason"],
                notes=r["notes"],
                previous_quantity=r["previous_quantity"],
                new_quantity=r["new_quantity"],
                adjustment_amount=r["adjustment_amount"],
                previous_price=r["previous_price"],
                new_price=r["new_price"],
                effective_date=r["effective_date"],
                timestamp=r["timestamp"]
            )
            for r in rows
        ]

    @staticmethod
    def get_recent_for_item_as_dicts(item_id: str, limit: int = 10):
        conn = get_connection()
        rows = conn.execute("""
            SELECT * FROM inventory_adjustment
            WHERE item_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (item_id, limit)).fetchall()
        conn.close()

        return [
            {
                "adjustment_id": r["adjustment_id"],
                "item_id": r["item_id"],
                "change_category": r["change_category"],
                "user_id": r["user_id"],
                "reason": r["reason"],
                "notes": r["notes"],
                "previous_quantity": r["previous_quantity"],
                "new_quantity": r["new_quantity"],
                "adjustment_amount": r["adjustment_amount"],
                "previous_price": r["previous_price"],
                "new_price": r["new_price"],
                "effective_date": r["effective_date"],
                "timestamp": r["timestamp"]
            }
            for r in rows
        ]

    @staticmethod
    def get_price_history_for_item(item_id: str):
        conn = get_connection()
        rows = conn.execute("""
            SELECT * FROM inventory_adjustment
            WHERE item_id = ? AND change_category = 'price_change'
            ORDER BY effective_date DESC
        """, (item_id,)).fetchall()
        conn.close()

        return [
            {
                "adjustment_id": r["adjustment_id"],
                "item_id": r["item_id"],
                "user_id": r["user_id"],
                "previous_price": r["previous_price"],
                "new_price": r["new_price"],
                "effective_date": r["effective_date"],
                "notes": r["notes"]
            }
            for r in rows
        ]

    def get_adjustment_summary(self) -> str:
        if self.change_category == "stock_adjustment":
            return (
                f"Stock Adjustment #{self.adjustment_id} | Item: {self.item_id} | "
                f"User: {self.user_id} | Prev Qty: {self.previous_quantity} | "
                f"New Qty: {self.new_quantity} | Change: {self.adjustment_amount} | "
                f"Reason: {self.reason} | Time: {self.timestamp}"
            )

        if self.change_category == "price_change":
            return (
                f"Price Change #{self.adjustment_id} | Item: {self.item_id} | "
                f"User: {self.user_id} | Prev Price: {self.previous_price} | "
                f"New Price: {self.new_price} | Effective: {self.effective_date}"
            )

        return f"Adjustment #{self.adjustment_id} | Item: {self.item_id}"

    def to_dict(self) -> dict:
        return {
            "adjustment_id": self.adjustment_id,
            "item_id": self.item_id,
            "change_category": self.change_category,
            "user_id": self.user_id,
            "reason": self.reason,
            "notes": self.notes,
            "previous_quantity": self.previous_quantity,
            "new_quantity": self.new_quantity,
            "adjustment_amount": self.adjustment_amount,
            "previous_price": self.previous_price,
            "new_price": self.new_price,
            "effective_date": self.effective_date,
            "timestamp": self.timestamp
        }
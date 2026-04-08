"""
SalesRecord <<Entity>>
Defines the SalesRecord class for tracking sales transactions imported from Zoho CSV
or created from direct sales processing.

This entity stores each sale line and provides methods to:
- create a sale record
- retrieve recent sales for an item
- retrieve sales as dictionaries for templates/controllers
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from database import get_connection


class SalesRecord:

    def __init__(
        self,
        sale_id: int = None,
        item_id: str = "",
        item_name: str = "",
        quantity_sold: int = 0,
        unit_price: float = 0.0,
        total_amount: float = 0.0,
        sale_source: str = "Zoho CSV Import",
        import_log_id: int = None,
        sold_by: str = "",
        timestamp: str = None
    ):
        self.sale_id = sale_id
        self.item_id = item_id
        self.item_name = item_name
        self.quantity_sold = quantity_sold
        self.unit_price = unit_price
        self.total_amount = total_amount if total_amount else quantity_sold * unit_price
        self.sale_source = sale_source
        self.import_log_id = import_log_id
        self.sold_by = sold_by
        self.timestamp = timestamp or datetime.now().isoformat()

    def create_entry(self) -> None:
        """Persist this sales record to the database."""
        self.validate()

        conn = get_connection()
        cursor = conn.execute("""
            INSERT INTO sales_record (
                item_id,
                item_name,
                quantity_sold,
                unit_price,
                total_amount,
                sale_source,
                import_log_id,
                sold_by,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.item_id,
            self.item_name,
            self.quantity_sold,
            self.unit_price,
            self.total_amount,
            self.sale_source,
            self.import_log_id,
            self.sold_by,
            self.timestamp
        ))
        self.sale_id = cursor.lastrowid
        conn.commit()
        conn.close()

    def validate(self) -> None:
        """Validate the sale before saving."""
        if not self.item_id:
            raise ValueError("item_id is required.")

        if not self.item_name:
            raise ValueError("item_name is required.")

        if self.quantity_sold <= 0:
            raise ValueError("quantity_sold must be greater than 0.")

        if self.unit_price < 0:
            raise ValueError("unit_price cannot be negative.")

        if self.total_amount < 0:
            raise ValueError("total_amount cannot be negative.")

    @staticmethod
    def create_sale(
        item_id: str,
        item_name: str,
        quantity_sold: int,
        unit_price: float,
        sale_source: str = "Zoho CSV Import",
        import_log_id: int = None,
        sold_by: str = ""
    ):
        """Create and persist a sales record."""
        sale = SalesRecord(
            item_id=item_id,
            item_name=item_name,
            quantity_sold=quantity_sold,
            unit_price=unit_price,
            total_amount=quantity_sold * unit_price,
            sale_source=sale_source,
            import_log_id=import_log_id,
            sold_by=sold_by
        )
        sale.create_entry()
        return sale

    @staticmethod
    def get_recent_for_item(item_id: str, limit: int = 10):
        """Return recent sales for a given item as SalesRecord objects."""
        conn = get_connection()
        rows = conn.execute("""
            SELECT * FROM sales_record
            WHERE item_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (item_id, limit)).fetchall()
        conn.close()

        return [
            SalesRecord(
                sale_id=r["sale_id"],
                item_id=r["item_id"],
                item_name=r["item_name"],
                quantity_sold=r["quantity_sold"],
                unit_price=r["unit_price"],
                total_amount=r["total_amount"],
                sale_source=r["sale_source"],
                import_log_id=r["import_log_id"],
                sold_by=r["sold_by"],
                timestamp=r["timestamp"]
            )
            for r in rows
        ]

    @staticmethod
    def get_recent_for_item_as_dicts(item_id: str, limit: int = 10):
        """Return recent sales for a given item as dictionaries."""
        conn = get_connection()
        rows = conn.execute("""
            SELECT * FROM sales_record
            WHERE item_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (item_id, limit)).fetchall()
        conn.close()

        return [
            {
                "sale_id": r["sale_id"],
                "item_id": r["item_id"],
                "item_name": r["item_name"],
                "quantity_sold": r["quantity_sold"],
                "unit_price": r["unit_price"],
                "total_amount": r["total_amount"],
                "sale_source": r["sale_source"],
                "import_log_id": r["import_log_id"],
                "sold_by": r["sold_by"],
                "timestamp": r["timestamp"]
            }
            for r in rows
        ]

    @staticmethod
    def get_recent_sales(limit: int = 20):
        """Return recent sales across all items."""
        conn = get_connection()
        rows = conn.execute("""
            SELECT * FROM sales_record
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,)).fetchall()
        conn.close()

        return [
            SalesRecord(
                sale_id=r["sale_id"],
                item_id=r["item_id"],
                item_name=r["item_name"],
                quantity_sold=r["quantity_sold"],
                unit_price=r["unit_price"],
                total_amount=r["total_amount"],
                sale_source=r["sale_source"],
                import_log_id=r["import_log_id"],
                sold_by=r["sold_by"],
                timestamp=r["timestamp"]
            )
            for r in rows
        ]

    def get_sale_summary(self) -> str:
        return (
            f"Sale #{self.sale_id} | Item: {self.item_id} ({self.item_name}) | "
            f"Qty Sold: {self.quantity_sold} | Unit Price: {self.unit_price:.2f} | "
            f"Total: {self.total_amount:.2f} | Source: {self.sale_source} | "
            f"Time: {self.timestamp}"
        )

    def to_dict(self) -> dict:
        return {
            "sale_id": self.sale_id,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "quantity_sold": self.quantity_sold,
            "unit_price": self.unit_price,
            "total_amount": self.total_amount,
            "sale_source": self.sale_source,
            "import_log_id": self.import_log_id,
            "sold_by": self.sold_by,
            "timestamp": self.timestamp
        }
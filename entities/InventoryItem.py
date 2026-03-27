"""
InventoryItem <<Entity>>
Shared across UC-001 (Import Daily Sales) and UC-002 (Check Item Availability).
Maps to InventoryItem on the combined class diagram.

UC-001 uses: deduct_quantity(), is_below_threshold(), update_price()
UC-002 uses: is_in_stock(), get_details(), matches_search(), get_availability_status()
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection


class InventoryItem:

    def __init__(self, item_id: str, item_name: str, unit_price: float,
                 stock_quantity: int, reorder_threshold: int,
                 grade: str = "", subject: str = "",
                 availability_status: str = "In Stock"):
        self.item_id = item_id
        self.item_name = item_name
        self.unit_price = unit_price
        self.stock_quantity = stock_quantity
        self.reorder_threshold = reorder_threshold
        self.grade = grade
        self.subject = subject
        self.availability_status = availability_status

    # ---- UC-001 Methods ----

    def deduct_quantity(self, amount: int) -> bool:
        """Deduct stock. Returns False if insufficient."""
        if amount < 0 or self.stock_quantity - amount < 0:
            return False
        self.stock_quantity -= amount
        self._update_availability_status()
        self._save()
        return True

    def is_below_threshold(self) -> bool:
        """Check if stock is at or below reorder threshold."""
        return self.stock_quantity <= self.reorder_threshold

    def update_price(self, new_price: float) -> None:
        """Update unit price."""
        self.unit_price = new_price
        self._save()

    # ---- UC-002 Methods ----

    def is_in_stock(self) -> bool:
        """Check if item has any stock available."""
        return self.stock_quantity > 0

    def get_details(self) -> dict:
        """Return full item details as dictionary."""
        return {
            "item_id": self.item_id,
            "item_name": self.item_name,
            "unit_price": self.unit_price,
            "stock_quantity": self.stock_quantity,
            "reorder_threshold": self.reorder_threshold,
            "grade": self.grade,
            "subject": self.subject,
            "availability_status": self.get_availability_status()
        }

    def matches_search(self, query: str) -> bool:
        """Check if this item matches a search query (by ID, name, grade, or subject)."""
        q = query.lower()
        return (q in self.item_id.lower() or
                q in self.item_name.lower() or
                q in self.grade.lower() or
                q in self.subject.lower())

    # ---- Shared Methods ----

    def get_availability_status(self) -> str:
        """Return current availability status string."""
        self._update_availability_status()
        return self.availability_status

    def _update_availability_status(self):
        if self.stock_quantity == 0:
            self.availability_status = "Out of Stock"
        elif self.is_below_threshold():
            self.availability_status = "Low Stock"
        else:
            self.availability_status = "In Stock"

    def _save(self):
        conn = get_connection()
        conn.execute("""
            UPDATE inventory_item
            SET stock_quantity = ?, availability_status = ?, unit_price = ?
            WHERE item_id = ?
        """, (self.stock_quantity, self.availability_status, self.unit_price, self.item_id))
        conn.commit()
        conn.close()

    # ---- Static Finders ----

    @staticmethod
    def find_by_id(item_id: str):
        conn = get_connection()
        row = conn.execute("SELECT * FROM inventory_item WHERE item_id = ?", (item_id,)).fetchone()
        conn.close()
        if row:
            return InventoryItem(
                item_id=row["item_id"], item_name=row["item_name"],
                unit_price=row["unit_price"], stock_quantity=row["stock_quantity"],
                reorder_threshold=row["reorder_threshold"], grade=row["grade"],
                subject=row["subject"], availability_status=row["availability_status"]
            )
        return None

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM inventory_item ORDER BY item_id").fetchall()
        conn.close()
        return [InventoryItem(
            item_id=r["item_id"], item_name=r["item_name"],
            unit_price=r["unit_price"], stock_quantity=r["stock_quantity"],
            reorder_threshold=r["reorder_threshold"], grade=r["grade"],
            subject=r["subject"], availability_status=r["availability_status"]
        ) for r in rows]

    @staticmethod
    def search(query: str):
        """Search inventory by any field. Returns matching InventoryItem objects."""
        all_items = InventoryItem.get_all()
        if not query or not query.strip():
            return all_items
        return [item for item in all_items if item.matches_search(query)]

    @staticmethod
    def filter_by_grade(grade: str):
        conn = get_connection()
        rows = conn.execute("SELECT * FROM inventory_item WHERE grade = ? ORDER BY item_id", (grade,)).fetchall()
        conn.close()
        return [InventoryItem(
            item_id=r["item_id"], item_name=r["item_name"],
            unit_price=r["unit_price"], stock_quantity=r["stock_quantity"],
            reorder_threshold=r["reorder_threshold"], grade=r["grade"],
            subject=r["subject"], availability_status=r["availability_status"]
        ) for r in rows]

    @staticmethod
    def filter_by_subject(subject: str):
        conn = get_connection()
        rows = conn.execute("SELECT * FROM inventory_item WHERE subject = ? ORDER BY item_id", (subject,)).fetchall()
        conn.close()
        return [InventoryItem(
            item_id=r["item_id"], item_name=r["item_name"],
            unit_price=r["unit_price"], stock_quantity=r["stock_quantity"],
            reorder_threshold=r["reorder_threshold"], grade=r["grade"],
            subject=r["subject"], availability_status=r["availability_status"]
        ) for r in rows]

    @staticmethod
    def create_new(item_id: str, item_name: str, unit_price: float,
                   stock_quantity: int = 0, reorder_threshold: int = 5,
                   grade: str = "", subject: str = ""):
        """Insert a brand-new inventory item into the database."""
        conn = get_connection()
        conn.execute("""
            INSERT INTO inventory_item
                (item_id, item_name, unit_price, stock_quantity, reorder_threshold, grade, subject, availability_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_id, item_name, unit_price, stock_quantity, reorder_threshold, grade, subject, "In Stock"))
        conn.commit()
        conn.close()
        return InventoryItem(item_id, item_name, unit_price, stock_quantity, reorder_threshold, grade, subject)

    def to_dict(self) -> dict:
        return self.get_details()

    def __repr__(self):
        return f"InventoryItem({self.item_id}, '{self.item_name}', qty={self.stock_quantity})"

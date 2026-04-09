"""
FavouriteItem <<Entity>>
Represents shared quick-access / favourited inventory items.

Used in UC-005: Access Frequently Used Items.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection


class FavouriteItem:

    def __init__(self, item_id: str, added_by: str, added_at: str):
        self.item_id = item_id
        self.added_by = added_by
        self.added_at = added_at

    @staticmethod
    def count() -> int:
        conn = get_connection()
        row = conn.execute("SELECT COUNT(*) AS count FROM favourite_item").fetchone()
        conn.close()
        return row["count"]

    @staticmethod
    def is_favourited(item_id: str) -> bool:
        conn = get_connection()
        row = conn.execute(
            "SELECT item_id FROM favourite_item WHERE item_id = ?",
            (item_id,)
        ).fetchone()
        conn.close()
        return row is not None

    @staticmethod
    def add(item_id: str, user_id: str) -> tuple[bool, str]:
        if FavouriteItem.is_favourited(item_id):
            return False, f"Item '{item_id}' is already in favourites."

        if FavouriteItem.count() >= 50:
            return False, "Favourites list is full (50 items). Please remove an item before adding more."

        conn = get_connection()
        conn.execute("""
            INSERT INTO favourite_item (item_id, added_by, added_at)
            VALUES (?, ?, ?)
        """, (item_id, user_id, datetime.now().isoformat(timespec="seconds")))
        conn.commit()
        conn.close()
        return True, f"Item '{item_id}' added to favourites."

    @staticmethod
    def remove(item_id: str) -> bool:
        conn = get_connection()
        cur = conn.execute("DELETE FROM favourite_item WHERE item_id = ?", (item_id,))
        conn.commit()
        deleted = cur.rowcount > 0
        conn.close()
        return deleted

    @staticmethod
    def get_all() -> list[dict]:
        """
        Returns favourites joined with live inventory data so stock quantity
        always reflects the current database state.
        """
        conn = get_connection()
        rows = conn.execute("""
            SELECT
            f.item_id,
            f.added_by,
            f.added_at,
            i.item_name,
            i.grade,
            i.unit_price,
            i.stock_quantity,
            i.reorder_threshold,
            i.availability_status,
            i.is_archived
            FROM favourite_item f
            JOIN inventory_item i ON i.item_id = f.item_id
            ORDER BY f.added_at DESC
            """).fetchall()
        conn.close()

        return [{
            "item_id": row["item_id"],
            "item_name": row["item_name"],
            "grade": row["grade"],
            "unit_price": row["unit_price"],
            "stock_quantity": row["stock_quantity"],
            "reorder_threshold": row["reorder_threshold"],
            "availability_status": row["availability_status"],
            "is_archived": row["is_archived"],
            "added_by": row["added_by"],
            "added_at": row["added_at"]
        } for row in rows]

    @staticmethod
    def get_all_ids() -> set[str]:
        conn = get_connection()
        rows = conn.execute("SELECT item_id FROM favourite_item").fetchall()
        conn.close()
        return {row["item_id"] for row in rows}
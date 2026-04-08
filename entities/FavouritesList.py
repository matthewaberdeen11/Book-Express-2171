"""
FavouritesList <<Entity>>
Stores staff's bookmarked items for quick access.
Maps to FavouritesList on the class diagram.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from database import get_connection


class FavouritesList:

    MAX_FAVOURITES = 50

    def __init__(self, favourite_id: int = None, user_id: str = "",
                 item_id: str = "", added_at: str = None):
        self.favourite_id = favourite_id
        self.user_id = user_id
        self.item_id = item_id
        self.added_at = added_at or datetime.now().isoformat()

    def add_to_favourites(self) -> bool:
        """Add item to favourites list. Returns False if list is full."""
        # Check if list is full
        count = FavouritesList.get_count(self.user_id)
        if count >= self.MAX_FAVOURITES:
            return False

        # Check duplicate
        if FavouritesList.is_favourite(self.user_id, self.item_id):
            return True  # Already exists, not an error

        conn = get_connection()
        cursor = conn.execute("""
            INSERT INTO favourites (user_id, item_id, added_at)
            VALUES (?, ?, ?)
        """, (self.user_id, self.item_id, self.added_at))
        self.favourite_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return True

    def remove_from_favourites(self) -> bool:
        """Remove item from favourites list."""
        conn = get_connection()
        conn.execute("""
            DELETE FROM favourites WHERE user_id = ? AND item_id = ?
        """, (self.user_id, self.item_id))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def is_favourite(user_id: str, item_id: str) -> bool:
        """Check if an item is already in the user's favourites."""
        conn = get_connection()
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM favourites WHERE user_id = ? AND item_id = ?",
            (user_id, item_id)
        ).fetchone()
        conn.close()
        return row["cnt"] > 0

    @staticmethod
    def get_count(user_id: str) -> int:
        """Get the number of favourites for a user."""
        conn = get_connection()
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM favourites WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        conn.close()
        return row["cnt"]

    @staticmethod
    def get_user_favourites(user_id: str) -> list:
        """Get all favourite items for a user with stock info."""
        conn = get_connection()
        rows = conn.execute("""
            SELECT f.favourite_id, f.item_id, f.added_at,
                   i.item_name, i.stock_quantity, i.unit_price,
                   i.reorder_threshold, i.availability_status
            FROM favourites f
            JOIN inventory_item i ON f.item_id = i.item_id
            WHERE f.user_id = ?
            ORDER BY f.added_at DESC
        """, (user_id,)).fetchall()
        conn.close()
        return [{
            "favourite_id": r["favourite_id"],
            "item_id": r["item_id"],
            "item_name": r["item_name"],
            "stock_quantity": r["stock_quantity"],
            "unit_price": r["unit_price"],
            "reorder_threshold": r["reorder_threshold"],
            "availability_status": r["availability_status"],
            "added_at": r["added_at"]
        } for r in rows]

    def to_dict(self) -> dict:
        return {
            "favourite_id": self.favourite_id,
            "user_id": self.user_id,
            "item_id": self.item_id,
            "added_at": self.added_at
        }

    def __repr__(self):
        return f"FavouritesList(user={self.user_id}, item={self.item_id})"
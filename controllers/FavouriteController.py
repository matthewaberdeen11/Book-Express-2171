"""
FavouriteController <<Control>>
Orchestrates UC-005: Access Frequently Used Items.

BCE flow:
Dashboard / SearchPage / ItemDetailView (Boundary)
    -> FavouriteController (Control)
    -> FavouriteItem / InventoryItem / AuditLog (Entities)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.FavouriteItem import FavouriteItem
from entities.InventoryItem import InventoryItem
from entities.AuditLog import AuditLog


class FavouriteController:

    def add_to_favourites(self, item_id: str, user_id: str = "staff_001") -> dict:
        item = InventoryItem.find_by_id(item_id)
        if item is None:
            return {"success": False, "error": f"Item '{item_id}' not found."}

        success, message = FavouriteItem.add(item_id, user_id)
        if not success:
            return {"success": False, "error": message}

        audit = AuditLog(
            user_id=user_id,
            action="add_to_favourites",
            details=f"Item '{item_id}' added to favourites"
        )
        audit.create_entry()

        return {"success": True, "message": message}

    def remove_from_favourites(self, item_id: str, user_id: str = "staff_001") -> dict:
        if not FavouriteItem.is_favourited(item_id):
            return {"success": False, "error": f"Item '{item_id}' is not in favourites."}

        removed = FavouriteItem.remove(item_id)
        if not removed:
            return {"success": False, "error": f"Unable to remove '{item_id}' from favourites."}

        audit = AuditLog(
            user_id=user_id,
            action="remove_from_favourites",
            details=f"Item '{item_id}' removed from favourites"
        )
        audit.create_entry()

        return {"success": True, "message": f"Item '{item_id}' removed from favourites."}

    def get_favourites(self) -> list[dict]:
        return FavouriteItem.get_all()

    def get_favourite_ids(self) -> set[str]:
        return FavouriteItem.get_all_ids()

    def is_favourited(self, item_id: str) -> bool:
        return FavouriteItem.is_favourited(item_id)
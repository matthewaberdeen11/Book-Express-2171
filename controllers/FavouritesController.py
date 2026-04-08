"""
FavouritesController <<Control>>
Orchestrates UC-005: Access Frequently Used Items workflow.

BCE flow: QuickAccessPanel (Boundary) → FavouritesController (Control) → Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.FavouritesList import FavouritesList
from entities.InventoryItem import InventoryItem
from entities.AuditLog import AuditLog


class FavouritesController:

    def __init__(self):
        self.current_user: str = ""

    def get_favourites(self, user_id: str = "staff_001") -> list:
        """
        Get all favourite items with current stock levels.
        Steps match UC-005 main flow:
        1. Retrieve favourites list for user
        2. Join with InventoryItem for live stock data
        3. Return items for Quick Access panel display
        """
        self.current_user = user_id
        return FavouritesList.get_user_favourites(user_id)

    def add_favourite(self, item_id: str, user_id: str = "staff_001") -> dict:
        """
        Add an item to the user's favourites.
        Maps to <<include>> Add to Favourites in UC-005.
        """
        self.current_user = user_id

        # Verify item exists
        item = InventoryItem.find_by_id(item_id)
        if item is None:
            return {"success": False, "error": f"Item '{item_id}' not found."}

        # Check list capacity
        count = FavouritesList.get_count(user_id)
        if count >= FavouritesList.MAX_FAVOURITES:
            return {
                "success": False,
                "error": "Favourites list is full (50 items). Please remove an item before adding more."
            }

        # Add to favourites
        fav = FavouritesList(user_id=user_id, item_id=item_id)
        success = fav.add_to_favourites()

        if success:
            audit = AuditLog(
                user_id=user_id,
                action="add_favourite",
                details=f"Added {item_id} ({item.item_name}) to favourites"
            )
            audit.create_entry()
            return {"success": True, "message": f"'{item.item_name}' added to favourites."}

        return {"success": False, "error": "Failed to add favourite."}

    def remove_favourite(self, item_id: str, user_id: str = "staff_001") -> dict:
        """
        Remove an item from the user's favourites.
        Maps to <<include>> Remove from Favourites in UC-005.
        """
        self.current_user = user_id

        fav = FavouritesList(user_id=user_id, item_id=item_id)
        fav.remove_from_favourites()

        audit = AuditLog(
            user_id=user_id,
            action="remove_favourite",
            details=f"Removed {item_id} from favourites"
        )
        audit.create_entry()

        return {"success": True, "message": "Item removed from favourites."}

    def is_favourite(self, item_id: str, user_id: str = "staff_001") -> bool:
        """Check if an item is in the user's favourites."""
        return FavouritesList.is_favourite(user_id, item_id)
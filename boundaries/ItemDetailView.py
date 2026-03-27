"""
ItemDetailView <<Boundary>>
Displays detailed item information to the user.
Delegates all business logic to SearchController.

BCE flow: ItemDetailView (Boundary) → SearchController (Control) → Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.SearchController import SearchController


class ItemDetailView:

    def __init__(self):
        self.current_item = None
        self.is_refreshing = False

    def display_details(self, item_id: str, user_id: str = "staff_001"):
        """
        Delegate to SearchController to get item details.
        This is the key BCE handoff: Boundary → Controller.
        Maps to <<include>> View Item Details in UC-002.
        """
        controller = SearchController()
        self.current_item = controller.get_item_details(item_id, user_id)
        return self.current_item

    def show_stock_status(self, quantity: int, status: str):
        """Display stock status with appropriate styling."""
        pass  # Handled by Flask template (item_detail.html)

    def refresh_on_inventory_change(self, item_id: str):
        """Check if item data has changed and refresh if needed."""
        self.is_refreshing = True
        controller = SearchController()
        from entities.InventoryItem import InventoryItem
        item = InventoryItem.find_by_id(item_id)
        if item:
            changed = controller.detect_inventory_change(item)
            if changed:
                self.current_item = controller.get_item_details(item_id)
            self.is_refreshing = False
            return changed
        self.is_refreshing = False
        return False
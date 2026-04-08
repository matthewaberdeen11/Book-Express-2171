"""
QuickAccessPanel <<Boundary>>
Handles the favourites/quick access panel on the dashboard.
Delegates all business logic to FavouritesController.

BCE flow: QuickAccessPanel (Boundary) → FavouritesController (Control) → Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.FavouritesController import FavouritesController


class QuickAccessPanel:

    def __init__(self):
        self.favourites = []
        self.status_message = ""

    def display_favourites(self, user_id: str = "staff_001"):
        """Load and return favourites for display in Quick Access panel."""
        controller = FavouritesController()
        self.favourites = controller.get_favourites(user_id)
        return self.favourites

    def add_to_favourites(self, item_id: str, user_id: str = "staff_001"):
        """Delegate add favourite to FavouritesController."""
        controller = FavouritesController()
        return controller.add_favourite(item_id, user_id)

    def remove_from_favourites(self, item_id: str, user_id: str = "staff_001"):
        """Delegate remove favourite to FavouritesController."""
        controller = FavouritesController()
        return controller.remove_favourite(item_id, user_id)

    def is_favourite(self, item_id: str, user_id: str = "staff_001") -> bool:
        """Check if item is in favourites."""
        controller = FavouritesController()
        return controller.is_favourite(item_id, user_id)

    def show_stock_badge(self, item):
        """Display stock level badge on favourite item."""
        pass  # Handled by Flask template

    
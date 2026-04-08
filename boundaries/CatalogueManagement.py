"""
CatalogueManagementPage <<Boundary>>
Handles interaction between Staff/Manager and catalogue management.
Delegates all business logic to CatalogueController.

BCE flow: CatalogueManagementPage (Boundary) → CatalogueController (Control) → Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.CatalogueController import CatalogueController


class CatalogueManagementPage:

    def __init__(self):
        self.current_action = None
        self.status_message = ""

    def add_new_book(self, item_id, item_name, unit_price, stock_quantity,
                     reorder_threshold, grade, subject, user_id="staff_001"):
        """Delegate add book to CatalogueController."""
        controller = CatalogueController()
        return controller.add_new_book(
            item_id, item_name, unit_price, stock_quantity,
            reorder_threshold, grade, subject, user_id
        )

    def update_book_details(self, item_id, item_name=None, unit_price=None,
                            grade=None, subject=None, user_id="staff_001"):
        """Delegate update to CatalogueController."""
        controller = CatalogueController()
        return controller.update_book_details(
            item_id, item_name, unit_price, grade, subject, user_id
        )

    def adjust_stock(self, item_id, adjustment_amount, reason,
                     notes="", user_id="staff_001"):
        """Delegate stock adjustment to CatalogueController."""
        controller = CatalogueController()
        return controller.adjust_stock(
            item_id, adjustment_amount, reason, notes, user_id
        )

    def display_form(self):
        """Display the appropriate form."""
        pass  # Handled by Flask template

    def show_success(self, message):
        """Display success message."""
        self.status_message = message

    def show_error(self, message):
        """Display error message."""
        self.status_message = message
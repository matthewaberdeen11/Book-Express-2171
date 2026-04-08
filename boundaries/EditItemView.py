"""
EditItemView <<Boundary>>
Displays and submits item edit information to the user.
Delegates all business logic to InventoryController.

BCE flow: EditItemView (Boundary) -> InventoryController (Control) -> Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.InventoryController import InventoryController


class EditItemView:

    def __init__(self):
        self.current_item = None
        self.last_submission_success = False
        self.validation_errors = []

    def load_item_for_edit(self, item_id: str, user_id: str = "staff_001"):
        controller = InventoryController()
        self.current_item = controller.get_item_for_edit(item_id, user_id)
        return self.current_item

    def submit_edit(self, item_id: str, form_data, user_id: str = "staff_001"):
        controller = InventoryController()

        update_data = {
            "item_name": form_data.get("item_name", "").strip(),
            "grade": form_data.get("grade", "").strip(),
            "subject": form_data.get("subject", "").strip(),
            "unit_price": form_data.get("unit_price", "").strip(),
            "adjustment_value": form_data.get("adjustment_value", "0").strip(),
            "adjustment_reason": form_data.get("adjustment_reason", "").strip(),
            "adjustment_notes": form_data.get("adjustment_notes", "").strip(),
            "is_archived": form_data.get("is_archived", "0").strip(),
        }

        success = controller.update_item(item_id, update_data, user_id)
        self.validation_errors = controller.get_validation_errors()
        self.last_submission_success = success

        if success:
            self.current_item = controller.get_item_for_edit(item_id, user_id)

        return success

    def get_validation_errors(self):
        return self.validation_errors
"""
CreateItemView <<Boundary>>
Displays and submits create-item information to the user.
Delegates all business logic to InventoryController.

BCE flow: CreateItemView (Boundary) -> InventoryController (Control) -> Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.InventoryController import InventoryController


class CreateItemView:

    def __init__(self):
        self.validation_errors = []
        self.last_submission_success = False

    def submit_create(self, form_data, user_id: str = "staff_001"):
        controller = InventoryController()

        create_data = {
            "item_id": form_data.get("item_id", "").strip(),
            "item_name": form_data.get("item_name", "").strip(),
            "grade": form_data.get("grade", "").strip(),
            "subject": form_data.get("subject", "").strip(),
            "unit_price": form_data.get("unit_price", "").strip(),
            "stock_quantity": form_data.get("stock_quantity", "0").strip(),
            "reorder_threshold": form_data.get("reorder_threshold", "5").strip(),
        }

        created_item = controller.create_item(create_data, user_id=user_id)
        self.validation_errors = controller.get_validation_errors()
        self.last_submission_success = created_item is not None

        return created_item

    def get_validation_errors(self):
        return self.validation_errors
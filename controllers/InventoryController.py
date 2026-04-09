"""
InventoryController <<Control>>
Orchestrates UC-003: Manage Inventory Records.

BCE flow:
EditItemView (Boundary) -> InventoryController (Control) -> Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.InventoryItem import InventoryItem
from entities.InventoryAdjustment import InventoryAdjustment
from entities.AuditLog import AuditLog


class InventoryController:

    def __init__(self):
        self.current_user: str = ""
        self.validation_errors: list[str] = []

    def get_item_for_edit(self, item_id: str, user_id: str = "staff_001") -> dict | None:
        """Load item details for the edit screen."""
        item = InventoryItem.find_by_id(item_id)
        if item is None:
            return None

        history_logs = InventoryAdjustment.get_recent_for_item_as_dicts(item_id)

        audit = AuditLog(
            user_id=user_id,
            action="view_edit_item",
            details=f"Opened edit view for: {item_id} ({item.item_name})"
        )
        audit.create_entry()

        item_with_history = item.get_details()
        item_with_history["history"] = history_logs
        return item_with_history

    def update_item(self, item_id: str, update_data: dict, user_id: str = "staff_001") -> bool:
        """
        Update catalogue fields and apply manual stock adjustment if provided.
        Also records price changes and inventory adjustment history.
        """
        self.current_user = user_id
        self.validation_errors = []

        item = InventoryItem.find_by_id(item_id)
        if item is None:
            self.validation_errors.append("Item not found.")
            return False

        self._validate_update(item, update_data)
        if self.validation_errors:
            return False
        
        is_archived = update_data.get("is_archived", "0") == "1"

        previous_quantity = item.stock_quantity
        previous_price = item.unit_price

        adjustment_value = int(update_data.get("adjustment_value", 0))
        new_quantity = previous_quantity + adjustment_value
        new_price = float(update_data["unit_price"])

        # 1. Update the inventory item itself
        item.update_catalogue_fields(
            item_name=update_data["item_name"],
            grade=update_data["grade"],
            subject=update_data["subject"],
            unit_price=new_price,
            stock_quantity=new_quantity,
            is_archived=is_archived
        )

        # 2. Record manual stock adjustment if one was made
        if adjustment_value != 0:
            InventoryAdjustment.create_stock_adjustment(
                item_id=item_id,
                user_id=user_id,
                previous_quantity=previous_quantity,
                new_quantity=new_quantity,
                reason=update_data["adjustment_reason"],
                notes=update_data.get("adjustment_notes", "").strip()
            )

        # 3. Record price history if price changed
        if float(previous_price) != float(new_price):
            price_note = "Price updated through Edit Item screen."

            user_note = update_data.get("adjustment_notes", "").strip()

            if user_note:
                price_note = f"{price_note} | Note: {user_note}"

            InventoryAdjustment.create_price_change(
                item_id=item_id,
                user_id=user_id,
                previous_price=previous_price,
                new_price=new_price,
                notes=price_note
            )

        # 4. Audit log
        audit_details = [
            f"Updated item: {item_id}",
            f"Name='{update_data['item_name']}'",
            f"Grade='{update_data['grade']}'",
            f"Subject='{update_data['subject']}'",
            f"Price: {previous_price} -> {new_price}"
        ]

        if adjustment_value != 0:
            audit_details.append(
                f"Stock: {previous_quantity} -> {new_quantity} "
                f"(change {adjustment_value}, reason='{update_data['adjustment_reason']}')"
            )

        audit = AuditLog(
            user_id=user_id,
            action="update_inventory_item",
            details=" | ".join(audit_details)
        )
        audit.create_entry()

        return True

    def _validate_update(self, item: InventoryItem, update_data: dict) -> None:
        """Validate all UC-003 edit rules."""
        item_name = update_data.get("item_name", "").strip()
        grade = update_data.get("grade", "").strip()
        subject = update_data.get("subject", "").strip()
        unit_price_raw = update_data.get("unit_price", "").strip()
        adjustment_value_raw = update_data.get("adjustment_value", "0").strip()
        adjustment_reason = update_data.get("adjustment_reason", "").strip()
        adjustment_notes = update_data.get("adjustment_notes", "").strip()
        is_archived = update_data.get("is_archived", "0").strip() == "1"

        if not item_name:
            self.validation_errors.append("Book name is required.")

        if not grade:
            self.validation_errors.append("Grade level is required.")

        if not subject:
            self.validation_errors.append("Subject category is required.")

        if not unit_price_raw:
            self.validation_errors.append("Unit price is required.")
        else:
            try:
                unit_price = float(unit_price_raw)
                if unit_price < 0:
                    self.validation_errors.append("Unit price cannot be negative.")
            except ValueError:
                self.validation_errors.append("Unit price must be a valid number.")

        try:
            adjustment_value = int(adjustment_value_raw) if adjustment_value_raw else 0
        except ValueError:
            self.validation_errors.append("Adjustment value must be a whole number.")
            return

        # AC-003.4
        if adjustment_value != 0 and not adjustment_reason:
            self.validation_errors.append("Adjustment reason is required")

        valid_reasons = ["Damaged", "Customer Return", "Stock Correction", "Theft/Loss", "Other"]
        if adjustment_reason and adjustment_reason not in valid_reasons:
            self.validation_errors.append("Adjustment reason is invalid.")

        if len(adjustment_notes) > 500:
            self.validation_errors.append("Adjustment notes cannot exceed 500 characters.")

        # AC-003.6
        attempted_final_quantity = item.stock_quantity + adjustment_value
        if attempted_final_quantity < 0:
            self.validation_errors.append(
                f"Adjustment would result in negative stock. "
                f"Attempted final quantity: {attempted_final_quantity}. "
                f"Current stock level: {item.stock_quantity}."
            )

        if is_archived and item.stock_quantity + adjustment_value != 0:
            self.validation_errors.append(
                "Item can only be archived when stock quantity is zero."
            )

    def delete_item(self, item_id: str, user_id: str = "staff_001") -> bool:
            """
            Delete an inventory item only if:
            - stock quantity is zero
            - there is no sales history

            Inventory adjustment history does not prevent deletion.
            """
            self.current_user = user_id
            self.validation_errors = []

            item = InventoryItem.find_by_id(item_id)
            if item is None:
                self.validation_errors.append("Item not found.")
                return False

            allowed, message = item.can_be_deleted()
            if not allowed:
                self.validation_errors.append(message)
                return False

            item_name = item.item_name
            item.delete()

            audit = AuditLog(
                user_id=user_id,
                action="delete_inventory_item",
                details=f"Deleted item: {item_id} ({item_name})"
            )
            audit.create_entry()

            return True
    
    def create_item(self, create_data: dict, user_id: str = "staff_001"):
        """
        Create a new catalogue entry for UC-003.
        """
        self.current_user = user_id
        self.validation_errors = []

        item_id = create_data.get("item_id", "").strip()
        item_name = create_data.get("item_name", "").strip()
        grade = create_data.get("grade", "").strip()
        subject = create_data.get("subject", "").strip()
        unit_price_raw = create_data.get("unit_price", "").strip()
        stock_quantity_raw = create_data.get("stock_quantity", "0").strip()
        reorder_threshold_raw = create_data.get("reorder_threshold", "5").strip()

        # required field validation
        if not item_id:
            self.validation_errors.append("Item ID is required.")
        if not item_name:
            self.validation_errors.append("Book name is required.")
        if not grade:
            self.validation_errors.append("Grade level is required.")
        if not subject:
            self.validation_errors.append("Subject category is required.")
        if not unit_price_raw:
            self.validation_errors.append("Unit price is required.")

        # unique item ID validation
        if item_id and InventoryItem.find_by_id(item_id) is not None:
            self.validation_errors.append(f"Item ID '{item_id}' already exists.")

        # numeric validation
        try:
            unit_price = float(unit_price_raw)
            if unit_price < 0:
                self.validation_errors.append("Unit price cannot be negative.")
        except ValueError:
            self.validation_errors.append("Unit price must be a valid number.")
            unit_price = 0.0

        try:
            stock_quantity = int(stock_quantity_raw) if stock_quantity_raw else 0
            if stock_quantity < 0:
                self.validation_errors.append("Stock quantity cannot be negative.")
        except ValueError:
            self.validation_errors.append("Stock quantity must be a valid integer.")
            stock_quantity = 0

        try:
            reorder_threshold = int(reorder_threshold_raw) if reorder_threshold_raw else 5
            if reorder_threshold < 0:
                self.validation_errors.append("Reorder threshold cannot be negative.")
        except ValueError:
            self.validation_errors.append("Reorder threshold must be a valid integer.")
            reorder_threshold = 5

        if self.validation_errors:
            return None

        new_item = InventoryItem.create_new(
            item_id=item_id,
            item_name=item_name,
            unit_price=unit_price,
            stock_quantity=stock_quantity,
            reorder_threshold=reorder_threshold,
            grade=grade,
            subject=subject
        )

        audit = AuditLog(
            user_id=user_id,
            action="create_inventory_item",
            details=(
                f"Created item: {item_id} ({item_name}) | "
                f"Grade='{grade}' | Subject='{subject}' | "
                f"Price={unit_price} | Stock={stock_quantity} | Threshold={reorder_threshold}"
            )
        )
        audit.create_entry()

        return new_item

    def get_validation_errors(self) -> list[str]:
        return self.validation_errors
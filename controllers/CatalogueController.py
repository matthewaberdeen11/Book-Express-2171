"""
CatalogueController <<Control>>
Orchestrates UC-003: Manage Inventory Records workflow.

BCE flow: CatalogueManagementPage (Boundary) → CatalogueController (Control) → Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from entities.InventoryItem import InventoryItem
from entities.AuditLog import AuditLog


class CatalogueController:

    def __init__(self):
        self.current_user: str = ""

    def add_new_book(self, item_id: str, item_name: str, unit_price: float,
                     stock_quantity: int, reorder_threshold: int,
                     grade: str, subject: str, user_id: str = "staff_001") -> dict:
        """
        Add a new book to the catalogue.
        Steps:
        1. Check if item_id already exists
        2. Validate required fields
        3. Create new InventoryItem
        4. Log the action via AuditLog
        """
        self.current_user = user_id

        # Step 1: Check duplicate
        existing = InventoryItem.find_by_id(item_id)
        if existing is not None:
            return {"success": False, "error": f"Item '{item_id}' already exists."}

        # Step 2: Validate
        if not item_name or not item_id:
            return {"success": False, "error": "Item ID and Name are required."}
        if unit_price < 0:
            return {"success": False, "error": "Price cannot be negative."}
        if stock_quantity < 0:
            return {"success": False, "error": "Quantity cannot be negative."}

        # Step 3: Create item
        item = InventoryItem(
            item_id=item_id, item_name=item_name,
            unit_price=unit_price, stock_quantity=stock_quantity,
            reorder_threshold=reorder_threshold,
            grade=grade, subject=subject
        )
        item.create()

        # Step 4: Log
        audit = AuditLog(
            user_id=user_id,
            action="add_new_book",
            details=f"Added: {item_id} ({item_name}) | Price: {unit_price} | Qty: {stock_quantity}"
        )
        audit.create_entry()

        return {"success": True, "message": f"Item '{item_id}' added successfully."}

    def update_book_details(self, item_id: str, item_name: str = None,
                            unit_price: float = None, grade: str = None,
                            subject: str = None, user_id: str = "staff_001") -> dict:
        """
        Update catalogue information for an existing book.
        Records previous values for audit trail.
        """
        self.current_user = user_id

        item = InventoryItem.find_by_id(item_id)
        if item is None:
            return {"success": False, "error": f"Item '{item_id}' not found."}

        # Track changes for audit
        changes = []

        if item_name is not None and item_name != item.item_name:
            old_name = item.item_name
            item.item_name = item_name
            changes.append(f"Name: '{old_name}' → '{item_name}'")

        if unit_price is not None and unit_price != item.unit_price:
            old_price = item.unit_price
            item.update_price(unit_price)
            changes.append(f"Price: {old_price} → {unit_price}")

        if grade is not None and grade != item.grade:
            old_grade = item.grade
            item.grade = grade
            changes.append(f"Grade: '{old_grade}' → '{grade}'")

        if subject is not None and subject != item.subject:
            old_subject = item.subject
            item.subject = subject
            changes.append(f"Subject: '{old_subject}' → '{subject}'")

        if not changes:
            return {"success": True, "message": "No changes detected."}

        item._save()

        # Log changes
        audit = AuditLog(
            user_id=user_id,
            action="update_book_details",
            details=f"Updated {item_id}: {'; '.join(changes)}"
        )
        audit.create_entry()

        return {"success": True, "message": f"Item '{item_id}' updated.", "changes": changes}

    def adjust_stock(self, item_id: str, adjustment_amount: int,
                     reason: str, notes: str = "",
                     user_id: str = "staff_001") -> dict:
        """
        Manually adjust stock for scenarios not captured by CSV import.
        Reasons: Damaged, Customer Return, Stock Correction, Theft/Loss, Other.
        """
        self.current_user = user_id

        # Validate reason
        valid_reasons = [
            "Damaged", "Customer Return", "Stock Correction",
            "Theft/Loss", "Inventory Adjustment", "Physical Stocktake",
            "System Correction", "Expired/Obsolete", "Other"
        ]
        if reason not in valid_reasons:
            return {"success": False, "error": "Adjustment reason is required."}

        item = InventoryItem.find_by_id(item_id)
        if item is None:
            return {"success": False, "error": f"Item '{item_id}' not found."}

        # Check permission (simplified - in full system would check user role)
        old_quantity = item.stock_quantity
        new_quantity = old_quantity + adjustment_amount

        # Prevent negative stock
        if new_quantity < 0:
            return {
                "success": False,
                "error": f"Adjustment would result in negative stock. Current: {old_quantity}, Adjustment: {adjustment_amount}"
            }

        # Apply adjustment
        item.stock_quantity = new_quantity
        item._update_availability_status()
        item._save()

        # Log with full audit trail
        audit = AuditLog(
            user_id=user_id,
            action="adjust_stock",
            details=(
                f"Stock adjusted for {item_id} ({item.item_name}): "
                f"{old_quantity} → {new_quantity} (adjustment: {adjustment_amount:+d}) | "
                f"Reason: {reason}"
                f"{' | Notes: ' + notes if notes else ''}"
            )
        )
        audit.create_entry()

        return {
            "success": True,
            "message": f"Stock adjusted for '{item_id}'.",
            "old_quantity": old_quantity,
            "new_quantity": new_quantity,
            "adjustment": adjustment_amount
        }
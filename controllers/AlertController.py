"""
AlertController <<Control>>
Orchestrates UC-004: Generate Low Stock Alert workflow.

BCE flow: AlertDashboard (Boundary) → AlertController (Control) → Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.InventoryItem import InventoryItem
from entities.LowStockAlert import LowStockAlert
from entities.AuditLog import AuditLog


class AlertController:

    def __init__(self):
        self.alerts_generated: int = 0
        self.items_scanned: int = 0

    def run_stock_check(self, user_id: str = "system") -> dict:
        """
        Scheduled stock evaluation - scans all items and generates alerts.
        Steps match UC-004 main flow:
        1. Retrieve all inventory records
        2. For each item, compare quantity to reorder threshold
        3. If below threshold and no existing alert, create alert
        4. Log the alert creation
        5. Return summary of scan
        """
        self.alerts_generated = 0
        self.items_scanned = 0

        all_items = InventoryItem.get_all()
        self.items_scanned = len(all_items)

        for item in all_items:
            # Step 2: Compare quantity to threshold
            if item.is_below_threshold():
                # Step 3: Check for duplicate
                if not LowStockAlert.is_duplicate(item.item_id):
                    # Create alert
                    alert = LowStockAlert(
                        item_id=item.item_id,
                        current_quantity=item.stock_quantity,
                        threshold=item.reorder_threshold
                    )
                    alert.create_alert()
                    self.alerts_generated += 1

                    # Step 4: Log
                    audit = AuditLog(
                        user_id=user_id,
                        action="low_stock_alert_created",
                        details=f"Alert for {item.item_id} ({item.item_name}): qty={item.stock_quantity}, threshold={item.reorder_threshold}"
                    )
                    audit.create_entry()

        return {
            "items_scanned": self.items_scanned,
            "alerts_generated": self.alerts_generated,
            "total_active_alerts": len(LowStockAlert.get_active_alerts())
        }

    def get_active_alerts(self) -> list:
        """Retrieve all active low stock alerts."""
        return LowStockAlert.get_active_alerts()

    def acknowledge_alert(self, alert_id: int, user_id: str = "staff_001") -> dict:
        """Mark an alert as acknowledged by staff."""
        alert = LowStockAlert.find_by_id(alert_id)
        if alert is None:
            return {"success": False, "error": "Alert not found."}

        alert.status = "acknowledged"
        alert._save()

        audit = AuditLog(
            user_id=user_id,
            action="alert_acknowledged",
            details=f"Alert #{alert_id} for {alert.item_id} acknowledged"
        )
        audit.create_entry()

        return {"success": True, "message": f"Alert #{alert_id} acknowledged."}

    def resolve_alert(self, alert_id: int, user_id: str = "staff_001") -> dict:
        """Resolve an alert (e.g. after restocking)."""
        alert = LowStockAlert.find_by_id(alert_id)
        if alert is None:
            return {"success": False, "error": "Alert not found."}

        alert.resolve_alert()

        audit = AuditLog(
            user_id=user_id,
            action="alert_resolved",
            details=f"Alert #{alert_id} for {alert.item_id} resolved"
        )
        audit.create_entry()

        return {"success": True, "message": f"Alert #{alert_id} resolved."}

    def configure_threshold(self, item_id: str, new_threshold: int,
                            user_id: str = "staff_001") -> dict:
        """
        Configure the reorder threshold for an item.
        Maps to <<include>> Configure Alert Threshold in UC-004.
        """
        if new_threshold < 0:
            return {"success": False, "error": "Threshold cannot be negative."}

        item = InventoryItem.find_by_id(item_id)
        if item is None:
            return {"success": False, "error": f"Item '{item_id}' not found."}

        old_threshold = item.reorder_threshold
        item.reorder_threshold = new_threshold
        item._update_availability_status()
        item._save()

        audit = AuditLog(
            user_id=user_id,
            action="configure_threshold",
            details=f"Threshold for {item_id}: {old_threshold} → {new_threshold}"
        )
        audit.create_entry()

        return {
            "success": True,
            "message": f"Threshold updated for '{item_id}'.",
            "old_threshold": old_threshold,
            "new_threshold": new_threshold
        }
"""
SearchController <<Control>>
Orchestrates UC-002: Check Item Availability workflow.
Maps to SearchController on the class diagram.

BCE flow: SearchPage/ItemDetailView (Boundary) -> SearchController (Control) -> Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.InventoryItem import InventoryItem
from entities.AuditLog import AuditLog
from entities.InventoryAdjustment import InventoryAdjustment
from entities.SalesRecord import SalesRecord


class SearchController:

    def __init__(self):
        self.current_user: str = ""
        self.last_search_query: str = ""
        self.search_results: list = []

    def search_inventory(self, query: str, user_id: str = "staff_001") -> list:
        """
        Main search workflow.
        Steps match UC-002 main flow:
        1. Receive search criteria from SearchPage (Boundary)
        2. Search InventoryItem entities
        3. Log the search action via AuditLog (Entity)
        4. Return matching items to Boundary for display
        """
        self.current_user = user_id
        self.last_search_query = query

        # Step 2: Search entities
        self.search_results = InventoryItem.search(query)

        # Step 3: Log the search
        audit = AuditLog(
            user_id=user_id,
            action="search_inventory",
            details=f"Query: '{query}' | Results: {len(self.search_results)}"
        )
        audit.create_entry()

        return self.search_results

    def filter_by_item_id(self, item_id: str) -> InventoryItem:
        """Look up a single item by exact ID."""
        return InventoryItem.find_by_id(item_id)

    def filter_by_name(self, name: str) -> list:
        """Filter inventory by name substring."""
        return [item for item in InventoryItem.get_all()
                if name.lower() in item.item_name.lower()]

    def filter_by_grade(self, grade: str) -> list:
        """Filter inventory by grade level."""
        return InventoryItem.filter_by_grade(grade)

    def filter_by_subject(self, subject: str) -> list:
        """Filter inventory by subject."""
        return InventoryItem.filter_by_subject(subject)

    def get_item_details(self, item_id: str, user_id: str = "staff_001") -> dict:
        """
        Get full details for a specific item.
        Maps to <<include>> View Item Details in UC-002.
        """
        item = InventoryItem.find_by_id(item_id)
        if item is None:
            return None

        adjustment_logs = InventoryAdjustment.get_recent_for_item_as_dicts(item_id)
        sales_logs = SalesRecord.get_recent_for_item_as_dicts(item_id)

        adjustment_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        sales_logs.sort(key=lambda x: x["timestamp"], reverse=True)

        audit = AuditLog(
            user_id=user_id,
            action="view_item_details",
            details=f"Viewed: {item_id} ({item.item_name})"
        )
        audit.create_entry()

        item_with_history = item.get_details()
        item_with_history["history"] = adjustment_logs
        item_with_history["sales_history"] = sales_logs

        return item_with_history

    def check_stock_status(self, item: InventoryItem) -> str:
        """Return stock status string for an item."""
        return item.get_availability_status()

    def detect_inventory_change(self, item: InventoryItem) -> bool:
        """Check if item data has changed since last retrieved (for auto-refresh)."""
        current = InventoryItem.find_by_id(item.item_id)
        if current is None:
            return True
        return current.stock_quantity != item.stock_quantity
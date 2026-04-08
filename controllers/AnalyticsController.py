"""
AnalyticsController <<Control>>
Orchestrates UC-006: View Business Insights workflow.

BCE flow: AnalyticsDashboard (Boundary) → AnalyticsController (Control) → Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.InventoryItem import InventoryItem
from entities.ImportLog import ImportLog
from entities.LowStockAlert import LowStockAlert
from entities.AuditLog import AuditLog
from database import get_connection


class AnalyticsController:

    def __init__(self):
        self.current_user: str = ""
        self.time_period: int = 30  # default 30 days

    def get_summary_statistics(self) -> dict:
        """
        Calculate and return dashboard summary statistics.
        Steps match UC-006 main flow step 2.
        """
        items = InventoryItem.get_all()
        alerts = LowStockAlert.get_active_alerts()

        total_items = len(items)
        in_stock = sum(1 for i in items if i.stock_quantity > 0)
        out_of_stock = sum(1 for i in items if i.stock_quantity == 0)
        total_value = sum(i.unit_price * i.stock_quantity for i in items)
        active_alerts = len(alerts)

        return {
            "total_items": total_items,
            "in_stock": in_stock,
            "out_of_stock": out_of_stock,
            "total_inventory_value": round(total_value, 2),
            "active_alerts": active_alerts
        }

    def get_top_sellers(self, limit: int = 10) -> list:
        """
        Get top selling items based on import data.
        Maps to <<include>> View Top Sellers in UC-006.
        """
        conn = get_connection()
        rows = conn.execute("""
            SELECT i.item_id, i.item_name, i.grade, i.subject,
                   i.unit_price, i.stock_quantity,
                   COALESCE(s.total_sold, 0) as total_sold
            FROM inventory_item i
            LEFT JOIN (
                SELECT item_id, SUM(quantity_sold) as total_sold
                FROM sales_record
                GROUP BY item_id
            ) s ON i.item_id = s.item_id
            ORDER BY total_sold DESC
            LIMIT ?
        """, (limit,)).fetchall()
        conn.close()

        # If sales_record table doesn't exist, fall back to basic listing
        if not rows:
            items = InventoryItem.get_all()
            return [{
                "item_id": i.item_id,
                "item_name": i.item_name,
                "grade": i.grade,
                "total_sold": 0
            } for i in items[:limit]]

        return [{
            "item_id": r["item_id"],
            "item_name": r["item_name"],
            "grade": r["grade"],
            "subject": r["subject"],
            "unit_price": r["unit_price"],
            "stock_quantity": r["stock_quantity"],
            "total_sold": r["total_sold"]
        } for r in rows]

    def get_sales_by_grade(self) -> list:
        """
        Aggregate sales data by grade level.
        Maps to <<include>> View Sales by Grade in UC-006.
        """
        items = InventoryItem.get_all()
        grade_data = {}

        for item in items:
            grade = item.grade or "Unknown"
            if grade not in grade_data:
                grade_data[grade] = {"grade": grade, "item_count": 0, "total_stock": 0, "total_value": 0}
            grade_data[grade]["item_count"] += 1
            grade_data[grade]["total_stock"] += item.stock_quantity
            grade_data[grade]["total_value"] += round(item.unit_price * item.stock_quantity, 2)

        return sorted(grade_data.values(), key=lambda x: x["grade"])

    def get_sales_by_subject(self) -> list:
        """Aggregate inventory data by subject."""
        items = InventoryItem.get_all()
        subject_data = {}

        for item in items:
            subject = item.subject or "Unknown"
            if subject not in subject_data:
                subject_data[subject] = {"subject": subject, "item_count": 0, "total_stock": 0, "total_value": 0}
            subject_data[subject]["item_count"] += 1
            subject_data[subject]["total_stock"] += item.stock_quantity
            subject_data[subject]["total_value"] += round(item.unit_price * item.stock_quantity, 2)

        return sorted(subject_data.values(), key=lambda x: x["subject"])

    def get_slow_movers(self, days: int = 90) -> list:
        """
        Get items with no sales in the specified period.
        Maps to <<include>> View Slow Movers in UC-006.
        """
        items = InventoryItem.get_all()
        # For now, identify items with high stock relative to threshold
        # In full implementation, would check against sales_record table
        slow_movers = []
        for item in items:
            if item.stock_quantity > 0:
                stock_ratio = item.stock_quantity / max(item.reorder_threshold, 1)
                if stock_ratio > 3:  # Stock is 3x above threshold = likely slow moving
                    slow_movers.append({
                        "item_id": item.item_id,
                        "item_name": item.item_name,
                        "grade": item.grade,
                        "stock_quantity": item.stock_quantity,
                        "reorder_threshold": item.reorder_threshold,
                        "stock_ratio": round(stock_ratio, 1)
                    })

        return sorted(slow_movers, key=lambda x: x["stock_ratio"], reverse=True)

    def get_import_history(self, limit: int = 10) -> list:
        """Get recent import activity for the analytics dashboard."""
        logs = ImportLog.get_recent(limit)
        return [log.to_dict() for log in logs]

    def change_time_period(self, days: int) -> None:
        """Change the analytics time period (7, 30, or 90 days)."""
        if days in [7, 30, 90]:
            self.time_period = days

    def get_full_dashboard(self, user_id: str = "staff_001") -> dict:
        """
        Get all analytics data for the full dashboard view.
        This is the main method called by the boundary.
        """
        self.current_user = user_id

        # Log dashboard view
        audit = AuditLog(
            user_id=user_id,
            action="view_analytics",
            details=f"Viewed analytics dashboard (period: {self.time_period} days)"
        )
        audit.create_entry()

        return {
            "summary": self.get_summary_statistics(),
            "by_grade": self.get_sales_by_grade(),
            "by_subject": self.get_sales_by_subject(),
            "slow_movers": self.get_slow_movers(),
            "import_history": self.get_import_history(),
            "time_period": self.time_period
        }
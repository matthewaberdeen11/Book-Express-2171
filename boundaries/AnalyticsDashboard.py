"""
AnalyticsDashboard <<Boundary>>
Displays analytics and business insights to managers.
Delegates all business logic to AnalyticsController.

BCE flow: AnalyticsDashboard (Boundary) → AnalyticsController (Control) → Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.AnalyticsController import AnalyticsController


class AnalyticsDashboard:

    def __init__(self):
        self.dashboard_data = None
        self.time_period = 30

    def load_dashboard(self, user_id: str = "staff_001"):
        """
        Load the full analytics dashboard.
        Delegates to AnalyticsController for all data.
        """
        controller = AnalyticsController()
        controller.change_time_period(self.time_period)
        self.dashboard_data = controller.get_full_dashboard(user_id)
        return self.dashboard_data

    def get_summary(self, user_id: str = "staff_001"):
        """Get just the summary statistics."""
        controller = AnalyticsController()
        return controller.get_summary_statistics()

    def get_top_sellers(self):
        """Get top selling items for bar chart."""
        controller = AnalyticsController()
        return controller.get_top_sellers()

    def get_sales_by_grade(self):
        """Get grade-level breakdown for chart."""
        controller = AnalyticsController()
        return controller.get_sales_by_grade()

    def get_sales_by_subject(self):
        """Get subject breakdown for chart."""
        controller = AnalyticsController()
        return controller.get_sales_by_subject()

    def get_slow_movers(self):
        """Get slow moving inventory."""
        controller = AnalyticsController()
        return controller.get_slow_movers()

    def change_time_period(self, days: int):
        """Change dashboard time period (7, 30, 90 days)."""
        self.time_period = days

    def refresh_dashboard(self, user_id: str = "staff_001"):
        """Refresh all dashboard data."""
        return self.load_dashboard(user_id)

    def display_charts(self):
        """Render charts on dashboard."""
        pass  # Handled by Flask template with Chart.js

    def display_summary(self):
        """Display summary statistics."""
        pass  # Handled by Flask template


    
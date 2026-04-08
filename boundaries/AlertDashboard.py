"""
AlertDashboard <<Boundary>>
Handles interaction between Manager and low stock alert system.
Delegates all business logic to AlertController.

BCE flow: AlertDashboard (Boundary) → AlertController (Control) → Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.AlertController import AlertController


class AlertDashboard:

    def __init__(self):
        self.status_message = ""

    def view_alerts(self):
        """Get all active alerts for display."""
        controller = AlertController()
        return controller.get_active_alerts()

    def run_stock_check(self):
        """Trigger a manual stock evaluation scan."""
        controller = AlertController()
        return controller.run_stock_check()

    def acknowledge_alert(self, alert_id, user_id="staff_001"):
        """Delegate acknowledge to AlertController."""
        controller = AlertController()
        return controller.acknowledge_alert(alert_id, user_id)

    def resolve_alert(self, alert_id, user_id="staff_001"):
        """Delegate resolve to AlertController."""
        controller = AlertController()
        return controller.resolve_alert(alert_id, user_id)

    def configure_threshold(self, item_id, new_threshold, user_id="staff_001"):
        """Delegate threshold config to AlertController."""
        controller = AlertController()
        return controller.configure_threshold(item_id, new_threshold, user_id)

    def display_alerts(self):
        """Display alert list."""
        pass  # Handled by Flask template

    def refresh_alerts(self):
        """Refresh the alert display."""
        return self.view_alerts()
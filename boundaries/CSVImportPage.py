"""
CSVImportPage <<Boundary>>
Handles interaction between Staff/Manager actor and the import system.
Delegates all business logic to ImportController.

BCE flow: CSVImportPage (Boundary) → ImportController (Control) → Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.ImportController import ImportController


class CSVImportPage:

    def __init__(self):
        self.selected_file = None
        self.status_message = ""
        self.is_loading = False

    def display_upload_form(self):
        """Display the CSV upload interface to the user."""
        pass  # Handled by Flask template (import.html)

    def select_file(self, file):
        """User selects a CSV file."""
        self.selected_file = file

    def trigger_import(self, file_content: str, user_id: str):
        """
        Delegate import processing to ImportController.
        This is the key BCE handoff: Boundary → Controller.
        """
        self.is_loading = True
        self.status_message = "Processing import..."

        controller = ImportController()
        report = controller.process_import(file_content, user_id)

        self.is_loading = False
        self.status_message = "Import complete."
        return report

    def display_report(self, report):
        """Display the import summary report to the user."""
        pass  # Handled by Flask template (report.html)

    def show_error(self, message: str):
        """Display an error message to the user."""
        self.status_message = message
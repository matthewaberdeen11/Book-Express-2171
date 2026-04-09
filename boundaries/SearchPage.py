"""
SearchPage <<Boundary>>
Handles search interface between Staff actor and the system.
Delegates all business logic to SearchController.

BCE flow: SearchPage (Boundary) → SearchController (Control) → Entities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.SearchController import SearchController
from controllers.FavouriteController import FavouriteController


class SearchPage:

    def __init__(self):
        self.search_query = ""
        self.results_visible = False
        self.selected_item = None

    def display_search_form(self):
        """Display the search interface to the user."""
        pass  # Handled by Flask template (search.html)

    def enter_search_criteria(self, query: str):
        """User enters a search query."""
        self.search_query = query

    def submit_search(self, query: str, user_id: str = "staff_001"):
        """
        Delegate search to SearchController.
        This is the key BCE handoff: Boundary → Controller.
        """
        self.search_query = query

        search_controller = SearchController()
        results = search_controller.search_inventory(query, user_id)
        self.results_visible = True
        
        favourite_ids = self.get_favourites()

        for item in results:
            item.is_favourited = item.item_id in favourite_ids

        return results

    def filter_by_grade(self, grade: str):
        """Delegate grade filter to SearchController."""
        controller = SearchController()
        results = controller.filter_by_grade(grade)

        favourite_ids = self.get_favourites()

        for item in results:
            item.is_favourited = item.item_id in favourite_ids

        return results

    def filter_by_subject(self, subject: str):
        """Delegate subject filter to SearchController."""
        controller = SearchController()
        results = controller.filter_by_subject(subject)

        favourite_ids = self.get_favourites()

        for item in results:
            item.is_favourited = item.item_id in favourite_ids

        return results

    def get_favourites(self):
        """Delegate to FavouriteController to get favourite items."""
        favourite_controller = FavouriteController()
        return favourite_controller.get_favourite_ids()

    def display_results(self, results):
        """Display search results to the user."""
        pass  # Handled by Flask template (search.html)

    def show_out_of_stock_label(self, item):
        """Mark an item as out of stock in the results."""
        pass  # Handled by Flask template via badge styling

    def auto_refresh_results(self):
        """Auto-refresh results when inventory changes."""
        pass  # implemented with JavaScript polling

    def show_error(self, message: str):
        """Display an error message to the user."""
        self.search_query = ""
        self.results_visible = False
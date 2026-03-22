from entities.ImportLog import ImportLog
from entities.ImportSummaryReport import ImportSummaryReport
from datetime import datetime

class ImportController:
    def __init__(self, adapter):
        self.adapter = adapter
        self.inventory = {} 

    def process_import(self, file_path):
        # Initialize the report
        raw_data = self.adapter.load_file(file_path)
        
        if not raw_data:
            return None
        summary = ImportSummaryReport(len(raw_data), 0, 0, [])
        
        for row in raw_data:
            try:
                item_data = self.adapter.transform_to_entity(row)
                # Logic to update inventory
                self.inventory[item_data['item_id']] = item_data
                summary.addSuccessfulImport()
            except Exception as e:
                summary.addError(str(e))
        
        # Create a log entry for the operation
        log = ImportLog(1, datetime.now(), "Completed", summary.getFormattedSummary())
        return summary

    
    def search_inventory(self, criteria):
        """  UC-002: Step 3 - Execute the search  """
        results = []
        search_term = criteria.lower()

        for item_id, item_data in self.inventory.items():
            # Check ID or Name (Step 3.1: handle incomplete IDs/names)
            if search_term in item_id.lower() or search_term in item_data['name'].lower():
                # Determine status for Step 6
                quantity = int(item_data['quantity'])
                status = "AVAILABLE" if quantity > 0 else "OUT OF STOCK"
                
                # Format result for the Boundary
                results.append({
                    "item_id": item_id,
                    "name": item_data['name'],
                    "quantity": quantity,
                    "status": status
                })
        return results

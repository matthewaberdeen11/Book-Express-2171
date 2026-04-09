"""
ImportController <<Control>>
Orchestrates UC-001: Import Daily Sales workflow.
Maps to ImportController on the class diagram.

BCE flow: CSVImportPage (Boundary) -> ImportController (Control) -> Entities
"""

import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from boundaries.ZohoCSVAdapter import ZohoCSVAdapter
from entities.InventoryItem import InventoryItem
from entities.ImportLog import ImportLog
from entities.ImportSummaryReport import ImportSummaryReport
from entities.LowStockAlert import LowStockAlert
from entities.InventoryAdjustment import InventoryAdjustment
from entities.SalesRecord import SalesRecord


class ImportController:

    PRICE_DISCREPANCY_THRESHOLD = 0.10

    def __init__(self):
        self.current_user: str = ""
        self.import_date: str = ""
        self.error_list: list = []
        self.unrecognised_items: list = []
        self.import_log_id: int = None

    def process_import(self, file_content: str, user_id: str) -> ImportSummaryReport:
        """
        Main workflow - orchestrates the entire CSV import.
        Steps match UC-001 main flow:
        1. Parse CSV via ZohoCSVAdapter (Boundary)
        2. Match each item_id to InventoryItem (Entity)
        3. Deduct quantity_sold from stock
        4. Check for low stock alerts
        5. Generate ImportSummaryReport (Entity)
        6. Create ImportLog entry (Entity)
        """
        self.current_user = user_id
        self.import_date = datetime.now().isoformat()
        report = ImportSummaryReport()

        # Step 1: Parse CSV
        adapter = ZohoCSVAdapter()
        try:
            records = adapter.extract_records(file_content)
        except ValueError as e:
            report.add_error(f"File validation failed: {str(e)}")
            return report

        for err in adapter.get_errors():
            report.add_error(err)

        report.total_processed = len(records)
        total_sales = 0.0
        sales_to_record = []  # Collect sales for batch processing after loop

        # Steps 2-4: Process each record
        for record in records:
            item_id = record["item_id"]
            qty = record["quantity_sold"]
            csv_price = record.get("average_price", 0)
            amount = record.get("amount", 0)

            # Step 2: Match item
            item = self.match_item(item_id)
            if item is None:
                report.add_unrecognised(record)
                continue

            # Step 3: Deduct stock
            if not self.deduct_stock(item, qty):
                report.add_error(f"Cannot deduct {qty} from {item_id} (stock: {item.stock_quantity})")
                continue
            else:
                sales_to_record.append((item, qty, amount))

            # Price discrepancy check (>10% difference)
            if csv_price > 0 and self.check_price_discrepancy(item, csv_price):
                report.add_price_discrepancy(item_id, item.item_name, item.unit_price, csv_price)

            total_sales += record.get("amount", item.unit_price * qty)
            report.add_success(item_id, item.item_name, qty)

            # Step 4: Check low stock
            self.check_low_stock(item)

        # Step 6: Log import
        self.log_import(report, file_content, total_sales)

        #Step 7: Record sales after processing all records to ensure log is created before sales records reference it
        for item, qty, amount in sales_to_record:
            self.record_sale(item, qty, amount)

        return report

    def match_item(self, item_id: str) -> InventoryItem:
        """Look up InventoryItem by ID."""
        return InventoryItem.find_by_id(item_id)

    def deduct_stock(self, item: InventoryItem, qty: int) -> bool:
        """Deduct quantity from item stock."""
        return item.deduct_quantity(qty)
    
    def record_sale(self, item: InventoryItem, qty: int, amount: float) -> None:
        """Create a SalesRecord entry and deduct stock."""

        sale = SalesRecord(
        item_id=item.item_id,
        item_name=item.item_name,
        quantity_sold=qty,
        unit_price=item.unit_price,
        total_amount=amount,
        sale_source="Zoho CSV Import",
        import_log_id=self.import_log_id,
        sold_by="system_import",
        timestamp=self.import_date
    )

        sale.create_entry()

    def check_price_discrepancy(self, item: InventoryItem, csv_price: float) -> bool:
        """Check if price differs by more than 10%."""
        if item.unit_price == 0:
            return False
        return abs(item.unit_price - csv_price) / item.unit_price > self.PRICE_DISCREPANCY_THRESHOLD

    def check_low_stock(self, item: InventoryItem) -> None:
        """Create alert if item is below threshold (no duplicates)."""
        if item.is_below_threshold() and not LowStockAlert.is_duplicate(item.item_id):
            alert = LowStockAlert(
                item_id=item.item_id,
                current_quantity=item.stock_quantity,
                threshold=item.reorder_threshold
            )
            alert.create_alert()

    def generate_report(self) -> ImportSummaryReport:
        return ImportSummaryReport()

    def log_import(self, report: ImportSummaryReport, filename: str, total_sales: float) -> ImportLog:
        """Create audit log entry for this import."""
        log = ImportLog(
            filename=filename[:100],
            user_id=self.current_user,
            total_sales_amount=total_sales,
            records_processed=report.total_processed,
            error_count=len(report.errors)
        )
        log.create_log()
        self.import_log_id = log.log_id
        return log

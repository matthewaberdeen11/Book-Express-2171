"""
ImportSummaryReport <<Entity>>
Stores results of a CSV import operation.
Maps to ImportSummaryReport on the class diagram.
"""


class ImportSummaryReport:

    def __init__(self):
        self.total_processed: int = 0
        self.successful_updates: list = []
        self.unrecognised_items: list = []
        self.errors: list = []
        self.price_discrepancies: list = []

    def add_success(self, item_id: str, item_name: str = "", quantity_sold: int = 0) -> None:
        self.successful_updates.append({
            "item_id": item_id, "item_name": item_name, "quantity_sold": quantity_sold
        })

    def add_error(self, error: str) -> None:
        self.errors.append(error)

    def add_unrecognised(self, record: dict) -> None:
        self.unrecognised_items.append(record)

    def add_price_discrepancy(self, item_id: str, item_name: str, system_price: float, csv_price: float) -> None:
        self.price_discrepancies.append({
            "item_id": item_id, "item_name": item_name,
            "system_price": system_price, "csv_price": csv_price
        })

    def get_formatted_summary(self) -> str:
        return (f"=== Import Summary ===\n"
                f"Total Processed: {self.total_processed}\n"
                f"Successful: {len(self.successful_updates)}\n"
                f"Unrecognised: {len(self.unrecognised_items)}\n"
                f"Price Discrepancies: {len(self.price_discrepancies)}\n"
                f"Errors: {len(self.errors)}")

    def to_dict(self) -> dict:
        return {
            "total_processed": self.total_processed,
            "successful_updates": self.successful_updates,
            "unrecognised_items": self.unrecognised_items,
            "errors": self.errors,
            "price_discrepancies": self.price_discrepancies,
            "success_count": len(self.successful_updates),
            "error_count": len(self.errors),
            "unrecognised_count": len(self.unrecognised_items),
            "price_discrepancy_count": len(self.price_discrepancies)
        }

    def __repr__(self):
        return f"ImportSummaryReport(processed={self.total_processed}, success={len(self.successful_updates)})"

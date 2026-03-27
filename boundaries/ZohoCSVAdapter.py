import csv
import io

class ZohoCSVAdapter:

    def __init__(self):
        self.errors = []

    def load_file(self, file_path):
        # Logic to read CSV from a file path
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                return list(csv.DictReader(file))
        except FileNotFoundError:
            print(f"\n[Error] The file '{file_path}' was not found. Please check the spelling.")
            return []
        except Exception as e:
            print(f"\n[Error] An unexpected error occurred: {e}")
            return []

    def extract_records(self, file_content: str) -> list:
        """
        Parse CSV content string into a list of dicts.
        Expected columns: item_id, quantity_sold (and optionally others).
        Called by ImportController.process_import().
        """
        self.errors = []
        records = []
        try:
            reader = csv.DictReader(io.StringIO(file_content))
            for i, row in enumerate(reader, start=1):
                try:
                    item_id = row.get("item_id", "").strip()
                    qty_raw = row.get("quantity_sold", "").strip()
                    price_raw = row.get("average_price", "").strip()
                    if not item_id:
                        self.errors.append(f"Row {i}: missing item_id")
                        continue
                    if not qty_raw:
                        self.errors.append(f"Row {i}: missing quantity_sold")
                        continue
                    records.append({
                        "item_id": item_id,
                        "quantity_sold": int(float(qty_raw)),
                        "average_price": float(price_raw) if price_raw else 0.0
                    })
                except ValueError:
                    self.errors.append(f"Row {i}: invalid quantity_sold '{qty_raw}'")
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {e}")
        return records

    def get_errors(self) -> list:
        """Return any row-level parsing errors from the last extract_records call."""
        return self.errors

    def transform_to_entity(self, row):
        # Maps Zoho column names to the Entity attributes
        return {
            'name': row.get('Item Name'),
            'quantity': int(row.get('Stock On Hand', 0)),
            'item_id': row.get('SKU')
        }

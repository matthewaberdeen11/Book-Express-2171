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

    REQUIRED_COLUMNS = {"item_id", "item_name", "quantity_sold"}

    def extract_records(self, file_content: str) -> list:
        """
        Parse ZOHO CSV content into a list of dicts.
        Expected columns: item_id, item_name, unit, is_combo_product,
                          quantity_sold, amount, average_price.
        Required columns: item_id, item_name, quantity_sold.
        """
        self.errors = []
        records = []
        try:
            reader = csv.DictReader(io.StringIO(file_content))
            # Validate required columns exist
            if reader.fieldnames:
                missing = self.REQUIRED_COLUMNS - set(reader.fieldnames)
                if missing:
                    raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

            for i, row in enumerate(reader, start=1):
                try:
                    item_id = row.get("item_id", "").strip()
                    item_name = row.get("item_name", "").strip()
                    qty_raw = row.get("quantity_sold", "").strip()

                    if not item_id:
                        self.errors.append(f"Row {i}: missing item_id")
                        continue
                    if not item_name:
                        self.errors.append(f"Row {i}: missing item_name")
                        continue
                    if not qty_raw:
                        self.errors.append(f"Row {i}: missing quantity_sold")
                        continue

                    records.append({
                        "item_id": item_id,
                        "item_name": item_name,
                        "unit": row.get("unit", "").strip(),
                        "is_combo_product": row.get("is_combo_product", "").strip().lower() == "true",
                        "quantity_sold": int(float(qty_raw)),
                        "amount": float(row.get("amount", "0").strip() or "0"),
                        "average_price": float(row.get("average_price", "0").strip() or "0"),
                    })
                except ValueError:
                    self.errors.append(f"Row {i}: invalid numeric value")
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

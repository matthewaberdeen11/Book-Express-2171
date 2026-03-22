import csv

class ZohoCSVAdapter:
    def load_file(self, file_path):
        # Logic to read CSV
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                return list(csv.DictReader(file))
        except FileNotFoundError:
            print(f"\n[Error] The file '{file_path}' was not found. Please check the spelling.")
            return [] # Return an empty list so the Controller doesn't crash
        except Exception as e:
            print(f"\n[Error] An unexpected error occurred: {e}")
            return []

    def transform_to_entity(self, row):
        # Maps Zoho column names to the Entity attributes
        return {
            'name': row.get('Item Name'),
            'quantity': int(row.get('Stock On Hand', 0)),
            'item_id': row.get('SKU')
        }

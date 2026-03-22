# boundaries/SearchPage.py

class SearchPage:
    def __init__(self, controller):
        self.controller = controller

    def display_search_interface(self):
        print("\n=== Check Item Availability ===")
        criteria = input("Enter Book Title or Item ID to search: ")
        
        results = self.controller.search_inventory(criteria)
        
        if not results:
            print(f"No matching items found for '{criteria}'.")
            return

        print(f"\nFound {len(results)} matching result(s):")
        print("-" * 50)
        # Step 5 & 6: Display results list with Out of Stock labels
        for item in results:
            status_display = f"[{item['status']}]" if item['status'] == "OUT OF STOCK" else f"Qty: {item['quantity']}"
            print(f"ID: {item['item_id']} | Name: {item['name']} | {status_display}")
        print("-" * 50)

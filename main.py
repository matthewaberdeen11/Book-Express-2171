# main.py
from boundaries.CSVImportPage import CSVImportPage
from boundaries.SearchPage import SearchPage
from boundaries.ZohoCSVAdapter import ZohoCSVAdapter
from controllers.ImportController import ImportController

def main():
    adapter = ZohoCSVAdapter()
    controller = ImportController(adapter)
    
    import_page = CSVImportPage(controller)
    search_page = SearchPage(controller)

    while True:
        print("\n--- Book Express Management System ---")
        print("1. Import Daily Sales")
        print("2. Check Item Availability")
        print("3. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            import_page.display_import_screen()
        elif choice == "2":
            search_page.display_search_interface()
        elif choice == "3":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()

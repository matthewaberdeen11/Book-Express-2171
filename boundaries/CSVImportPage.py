class CSVImportPage:
    def __init__(self, controller):
        self.controller = controller

    def display_import_screen(self):
        print("--- Book Express CSV Import ---")
        file_path = input("Enter the path to the CSV file: ")
        
        print("Processing...")
        report = self.controller.process_import(file_path)
        
        print("\nImport Finished!")
        print(report.getFormattedSummary())
    
        if report:
            print("\nImport Finished!")
            print(report.getFormattedSummary())
        else:
            print("\nImport aborted: No data was processed.")

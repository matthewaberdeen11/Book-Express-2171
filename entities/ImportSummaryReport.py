class ImportSummaryReport:
    def __init__(self, total_records, successful_imports, failed_imports, error_details):
        self.total_records = total_records
        self.successful_imports = successful_imports
        self.failed_imports = failed_imports
        self.error_details = error_details

    def addSuccessfulImport(self):
        self.successful_imports += 1
    
    def addError(self, error_message):
        self.failed_imports += 1
        self.error_details.append(error_message)
    
    def addUnrecognizedItem(self, itemId):
        self.failed_imports += 1
        self.error_details.append(f"Unrecognized item ID: {itemId}")
    
    def getFormattedSummary(self):
        return (f"Import Summary:\n"
                f"Total Records: {self.total_records}\n"
                f"Successful Imports: {self.successful_imports}\n"
                f"Failed Imports: {self.failed_imports}\n"
                f"Error Details: {', '.join(self.error_details)}")

    def __str__(self):
        return (f"ImportSummaryReport(total_records={self.total_records}, "
                f"successful_imports={self.successful_imports}, "
                f"failed_imports={self.failed_imports}, "
                f"error_details={self.error_details})")
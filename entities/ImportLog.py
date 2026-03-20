class ImportLog:
    def __init__(self, import_id, timestamp, status, details):
        self.import_id = import_id
        self.timestamp = timestamp
        self.status = status
        self.details = details

    def __str__(self):
        return f"ImportLog(import_id={self.import_id}, timestamp='{self.timestamp}', status='{self.status}', details='{self.details}')"
    
    def createLogEntry(self):
         ImportLog.logs.append(self)
    
    def getLogSummary(self):
        return f"Import ID: {self.import_id}, Status: {self.status}, Timestamp: {self.timestamp}"
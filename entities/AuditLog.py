class AuditLog:
    def __init__(self, id, action, timestamp, user_id):
        self.id = id
        self.action = action
        self.timestamp = timestamp
        self.user_id = user_id

    def __str__(self):
        return f"AuditLog(id={self.id}, action='{self.action}', timestamp='{self.timestamp}', user_id={self.user_id})"
    
    def createEntry(self):
        AuditLog.logs.append(self)

    def getLogSummary(self):
        return f"Audit Log - ID: {self.id}, Action: {self.action}, Timestamp: {self.timestamp}, User ID: {self.user_id}"
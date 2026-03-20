class LowStockAlert:
    def __init__(self, product_id, product_name, current_stock):
        self.product_id = product_id
        self.product_name = product_name
        self.current_stock = current_stock


    def createAlert(self):
         LowStockAlert.alerts.append(self)
    
    def isDuplicate(self, other_alert):
        return self.product_id == other_alert.product_id and self.current_stock == other_alert.current_stock

    def __str__(self):
        return f"LowStockAlert(product_id={self.product_id}, product_name='{self.product_name}', current_stock={self.current_stock})"
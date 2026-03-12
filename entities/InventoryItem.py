class  InventoryItem:
    def __init__(self, name, quantity, item_id):
        self.name = name
        self.quantity = quantity
        self.item_id = item_id

    def deduct_quantity(self, amount):
        if amount > self.quantity:
            raise ValueError("Not enough quantity in inventory")
        self.quantity -= amount
        return True
    
    def is_below_threshold(self, threshold = 10):
        return self.quantity <= threshold
    
    def updatePrice(self, new_price):
        self.price = new_price
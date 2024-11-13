# models.py
class User:
    def __init__(self, username, password, role='guest'):
        self.username = username
        self.password = password
        self.role = role  # 'admin', 'user', or 'guest'

class FencingEquipment:
    def __init__(self, name, description, price, stock, blade_length, material, weight, brand):
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.blade_length = blade_length
        self.material = material
        self.weight = weight
        self.brand = brand

class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, product, quantity):
        self.items.append((product, quantity))

    def total_price(self):
        return sum(item.price * quantity for item, quantity in self.items)

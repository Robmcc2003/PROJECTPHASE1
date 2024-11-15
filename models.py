# models.py
class User:
    def __init__(self, username, password, role='guest'):
        self.username = username
        self.password = password
        self.role = role  # 'admin', 'user', or 'guest'


class FencingEquipment:
    def __init__(self, name, description, type, price, stock, blade_length=None, material=None, weight=None, size=None, color=None, padding_level=None, brand=None, image_url=None, delivery_fee=0.0):
        self.name = name
        self.description = description
        self.type = type  # "Blade" or "Jacket"
        self.price = price
        self.stock = stock
        self.blade_length = blade_length  # Blade-specific
        self.material = material
        self.weight = weight  # Blade-specific
        self.size = size  # Jacket-specific
        self.color = color  # Jacket-specific
        self.padding_level = padding_level  # Jacket-specific
        self.brand = brand
        self.image_url = image_url
        self.delivery_fee = delivery_fee



class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, product, quantity):
        self.items.append((product, quantity))

    def total_price(self):
        return sum(item.price * quantity for item, quantity in self.items)

class Sale:
    def __init__(self, date, items, total):
        self.date = date
        self.items = items  # List of dictionaries: [{"name": ..., "quantity": ..., "price": ...}]
        self.total = total

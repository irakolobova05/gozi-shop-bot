class Product:
    def __init__(self, id, name, category, description, price, images,status, shop_id, sizes):
        self.id = id
        self.name = name
        self.category = category
        self.description = description
        self.price = price
        self.images = images
        self.status = status
        self.shop_id = shop_id
        self.sizes = sizes

class Shop:
    def __init__(self, id, name, description, images, status):
        self.id = id
        self.name = name
        self.description = description
        self.images = images
        self.status = status

class Category:
    def __init__(self, id, name):
        self.id = id
        self.name = name
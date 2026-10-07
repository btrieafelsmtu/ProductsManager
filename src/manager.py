from constants import (
    FILTER_ALL,
    FILTER_EXPIRED,
    FILTER_SOON,
    STATE_EXPIRED,
    STATE_SOON,
)
from products import Product
from storage import ProductStorage


class ProductManager:
    def __init__(self, storage: ProductStorage) -> None:
        self.storage: ProductStorage = storage
        self.products: list[Product] = self.storage.load_products()

    def add_product(self, product: Product) -> None:
        self.products.append(product)
        self.save()

    def delete_product(self, product_id: str) -> None:
        self.products = [
            product for product in self.products if product.product_id != product_id
        ]
        self.save()

    def increase_quantity(self, product_id: str) -> None:
        product = self.find_product(product_id)
        if product is not None:
            product.increase_quantity()
            self.save()

    def decrease_quantity(self, product_id: str) -> None:
        product = self.find_product(product_id)
        if product is not None:
            product.decrease_quantity()
            self.save()

    def find_product(self, product_id: str) -> Product | None:
        for product in self.products:
            if product.product_id == product_id:
                return product
        return None

    def get_filtered_products(self, filter_type: str = FILTER_ALL) -> list[Product]:
        if filter_type == FILTER_SOON:
            return [
                product
                for product in self.products
                if product.get_state() == STATE_SOON
            ]
        if filter_type == FILTER_EXPIRED:
            return [
                product
                for product in self.products
                if product.get_state() == STATE_EXPIRED
            ]
        return list(self.products)

    def save(self) -> None:
        self.storage.save_products(self.products)

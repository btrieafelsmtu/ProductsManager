import json
from datetime import date
from pathlib import Path

from constants import (
    PRODUCT_TYPE_PERISHABLE,
    PRODUCT_TYPE_REGULAR,
)
from products import PerishableProduct, Product, RegularProduct


class ProductStorage:
    def __init__(self, file_path: Path) -> None:
        self.file_path: Path = file_path

    def load_products(self) -> list[Product]:
        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open(encoding="utf-8") as file:
                records = json.load(file)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return []

        if not isinstance(records, list):
            return []

        products: list[Product] = []
        for record in records:
            product = self._create_product(record)
            if product is not None:
                products.append(product)
        return products

    def save_products(self, products: list[Product]) -> None:
        records = [product.to_dict() for product in products]
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(records, file, ensure_ascii=False, indent=2)

    def _create_product(self, record: dict) -> Product | None:
        try:
            product_type = record["type"]
            product_id = str(record["product_id"])
            name = str(record["name"]).strip()
            quantity = int(record["quantity"])
            if not name or quantity < 0:
                return None
            if product_type == PRODUCT_TYPE_PERISHABLE:
                expiration_date = date.fromisoformat(str(record["expiration_date"]))
                return PerishableProduct(name, quantity, expiration_date, product_id)
            if product_type == PRODUCT_TYPE_REGULAR:
                return RegularProduct(name, quantity, product_id)
        except (KeyError, TypeError, ValueError, OverflowError):
            return None
        return None

import uuid
from datetime import date

from constants import (
    DATE_FORMAT_DISPLAY,
    EXPIRATION_WARNING_DAYS,
    PRODUCT_TYPE_PERISHABLE,
    PRODUCT_TYPE_REGULAR,
    STATE_EXPIRED,
    STATE_NOT_TRACKED,
    STATE_OK,
    STATE_SOON,
    STATE_UNKNOWN,
    TYPE_PERISHABLE_TITLE,
    TYPE_REGULAR_TITLE,
)


class Product:
    def __init__(self, name: str, quantity: int, product_id: str | None = None) -> None:
        self.product_id: str = product_id if product_id else str(uuid.uuid4())
        self.name: str = name
        self.quantity: int = quantity

    def increase_quantity(self) -> None:
        self.quantity += 1

    def decrease_quantity(self) -> None:
        self.quantity -= 1
        if self.quantity < 0:
            self.quantity = 0

    def get_description(self) -> str:
        return (
            f"{self.get_type_name()} продукт: "
            f"{self.name}, количество: {self.quantity}"
        )

    def get_state(self) -> str:
        return STATE_UNKNOWN

    def get_type_name(self) -> str:
        return TYPE_REGULAR_TITLE

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "quantity": self.quantity,
        }


class RegularProduct(Product):
    def __init__(self, name: str, quantity: int, product_id: str | None = None) -> None:
        super().__init__(name, quantity, product_id)

    def get_state(self) -> str:
        return STATE_NOT_TRACKED

    def to_dict(self) -> dict:
        record = super().to_dict()
        record["type"] = PRODUCT_TYPE_REGULAR
        return record


class PerishableProduct(Product):
    def __init__(
        self,
        name: str,
        quantity: int,
        expiration_date: date,
        product_id: str | None = None,
    ) -> None:
        super().__init__(name, quantity, product_id)
        self.expiration_date: date = expiration_date

    def get_description(self) -> str:
        return (
            f"{super().get_description()}, "
            f"срок годности до {self.get_expiration_date_text()}"
        )

    def get_state(self) -> str:
        days_left = (self.expiration_date - date.today()).days
        if days_left < 0:
            return STATE_EXPIRED
        if days_left <= EXPIRATION_WARNING_DAYS:
            return STATE_SOON
        return STATE_OK

    def get_expiration_date_text(self) -> str:
        return self.expiration_date.strftime(DATE_FORMAT_DISPLAY)

    def get_type_name(self) -> str:
        return TYPE_PERISHABLE_TITLE

    def to_dict(self) -> dict:
        record = super().to_dict()
        record["type"] = PRODUCT_TYPE_PERISHABLE
        record["expiration_date"] = self.expiration_date.isoformat()
        return record

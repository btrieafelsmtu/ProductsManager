from collections.abc import Callable
from datetime import date, datetime

import flet as ft

from constants import (
    APP_TITLE,
    EMPTY_LIST_MESSAGE,
    EXPIRATION_INVALID_MESSAGE,
    EXPIRATION_REQUIRED_MESSAGE,
    FILTER_ALL,
    FILTER_ALL_TITLE,
    FILTER_EXPIRED,
    FILTER_EXPIRED_TITLE,
    FILTER_SOON,
    FILTER_SOON_TITLE,
    NAME_REQUIRED_MESSAGE,
    PRODUCT_TYPE_PERISHABLE,
    PRODUCT_TYPE_REGULAR,
    QUANTITY_INVALID_MESSAGE,
    TYPE_PERISHABLE_TITLE,
    TYPE_REGULAR_TITLE,
)
from manager import ProductManager
from products import PerishableProduct, Product, RegularProduct


class ProductCard:
    def __init__(
        self,
        product: Product,
        on_increase: Callable[[str], None],
        on_decrease: Callable[[str], None],
        on_delete: Callable[[str], None],
    ) -> None:
        self.product: Product = product
        self.on_increase: Callable[[str], None] = on_increase
        self.on_decrease: Callable[[str], None] = on_decrease
        self.on_delete: Callable[[str], None] = on_delete

    def build(self) -> ft.Card:
        title = ft.Text(value=self.product.name, size=16, weight=ft.FontWeight.BOLD)
        info_controls: list[ft.Text] = [
            ft.Text(value=f"Количество: {self.product.quantity}"),
            ft.Text(value=f"Тип: {self.product.get_type_name()}"),
        ]
        if isinstance(self.product, PerishableProduct):
            info_controls.append(
                ft.Text(
                    value=f"Срок годности: {self.product.get_expiration_date_text()}"
                )
            )
            info_controls.append(
                ft.Text(value=f"Состояние: {self.product.get_state()}")
            )

        actions = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.REMOVE,
                    tooltip="Уменьшить количество",
                    on_click=lambda event: self.on_decrease(self.product.product_id),
                ),
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    tooltip="Увеличить количество",
                    on_click=lambda event: self.on_increase(self.product.product_id),
                ),
                ft.TextButton(
                    content="Удалить",
                    on_click=lambda event: self.on_delete(self.product.product_id),
                ),
            ],
            spacing=5,
        )

        return ft.Card(
            content=ft.Container(
                content=ft.Column(controls=[title, *info_controls, actions], spacing=4),
                padding=10,
            )
        )


class ProductApp:
    def __init__(self, page: ft.Page, manager: ProductManager) -> None:
        self.page: ft.Page = page
        self.manager: ProductManager = manager
        self.current_filter: str = FILTER_ALL

        self.name_field = ft.TextField(
            label="Название", hint_text="Например: молоко", width=220
        )
        self.quantity_field = ft.TextField(
            label="Количество",
            hint_text="Например: 2",
            width=160,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.type_dropdown = ft.Dropdown(
            label="Тип продукта",
            width=220,
            value=PRODUCT_TYPE_REGULAR,
            options=[
                ft.DropdownOption(
                    key=PRODUCT_TYPE_REGULAR, text=TYPE_REGULAR_TITLE
                ),
                ft.DropdownOption(
                    key=PRODUCT_TYPE_PERISHABLE, text=TYPE_PERISHABLE_TITLE
                ),
            ],
            on_select=self.on_type_select,
        )
        self.expiration_field = ft.TextField(
            label="Срок годности",
            hint_text="Формат: ДД-ММ-ГГГГ",
            width=220,
            disabled=True,
        )
        self.add_button = ft.Button(
            content="Добавить", icon=ft.Icons.ADD, on_click=self.on_add_product_click
        )
        self.message_text = ft.Text(value="")
        self.product_list = ft.Column(controls=[])

        self.build_page()

    def build_page(self) -> None:
        self.page.title = APP_TITLE
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.add(
            ft.Text(value=APP_TITLE, size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.build_add_form(),
            self.message_text,
            ft.Divider(),
            self.build_filters_row(),
            self.product_list,
        )
        self.refresh_product_list()

    def build_add_form(self) -> ft.Column:
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[self.name_field, self.quantity_field],
                    wrap=True,
                ),
                ft.Row(
                    controls=[self.type_dropdown, self.expiration_field],
                    wrap=True,
                ),
                self.add_button,
            ],
            spacing=8,
        )

    def build_filters_row(self) -> ft.Row:
        return ft.Row(
            controls=[
                ft.TextButton(
                    content=FILTER_ALL_TITLE, on_click=self.on_show_all_click
                ),
                ft.TextButton(
                    content=FILTER_SOON_TITLE, on_click=self.on_show_soon_click
                ),
                ft.TextButton(
                    content=FILTER_EXPIRED_TITLE,
                    on_click=self.on_show_expired_click,
                ),
            ],
            wrap=True,
        )

    def refresh_product_list(self) -> None:
        products = self.manager.get_filtered_products(self.current_filter)
        if not products:
            self.product_list.controls = [ft.Text(value=EMPTY_LIST_MESSAGE)]
        else:
            self.product_list.controls = [
                ProductCard(
                    product,
                    self.increase_product,
                    self.decrease_product,
                    self.delete_product,
                ).build()
                for product in products
            ]
        self.page.update()

    def add_product_from_form(self) -> None:
        name = (self.name_field.value or "").strip()
        if not name:
            self.show_message(NAME_REQUIRED_MESSAGE)
            return

        try:
            quantity = int((self.quantity_field.value or "").strip())
        except ValueError:
            self.show_message(QUANTITY_INVALID_MESSAGE)
            return
        if quantity <= 0:
            self.show_message(QUANTITY_INVALID_MESSAGE)
            return

        product: Product
        if self.type_dropdown.value == PRODUCT_TYPE_PERISHABLE:
            expiration_text = (self.expiration_field.value or "").strip()
            if not expiration_text:
                self.show_message(EXPIRATION_REQUIRED_MESSAGE)
                return
            expiration_date = self.parse_expiration_date(expiration_text)
            if expiration_date is None:
                self.show_message(EXPIRATION_INVALID_MESSAGE)
                return
            product = PerishableProduct(name, quantity, expiration_date)
        else:
            product = RegularProduct(name, quantity)

        self.manager.add_product(product)
        self.clear_form()
        self.refresh_product_list()
        self.show_message(f"Добавлен продукт: {product.get_description()}")

    def parse_expiration_date(self, value: str) -> date | None:
        try:
            return datetime.strptime(value.strip(), "%d-%m-%Y").date()
        except ValueError:
            return None

    def clear_form(self) -> None:
        self.name_field.value = ""
        self.quantity_field.value = ""
        self.expiration_field.value = ""

    def show_message(self, message: str) -> None:
        self.message_text.value = message
        self.page.update()

    def increase_product(self, product_id: str) -> None:
        self.manager.increase_quantity(product_id)
        self.refresh_product_list()

    def decrease_product(self, product_id: str) -> None:
        self.manager.decrease_quantity(product_id)
        self.refresh_product_list()

    def delete_product(self, product_id: str) -> None:
        self.manager.delete_product(product_id)
        self.refresh_product_list()

    def set_filter(self, filter_type: str) -> None:
        self.current_filter = filter_type
        self.refresh_product_list()

    def on_add_product_click(self, event: ft.ControlEvent) -> None:
        self.add_product_from_form()

    def on_type_select(self, event: ft.ControlEvent) -> None:
        self.expiration_field.disabled = (
            self.type_dropdown.value != PRODUCT_TYPE_PERISHABLE
        )
        self.page.update()

    def on_show_all_click(self, event: ft.ControlEvent) -> None:
        self.set_filter(FILTER_ALL)

    def on_show_soon_click(self, event: ft.ControlEvent) -> None:
        self.set_filter(FILTER_SOON)

    def on_show_expired_click(self, event: ft.ControlEvent) -> None:
        self.set_filter(FILTER_EXPIRED)

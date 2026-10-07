import flet as ft

from constants import PRODUCTS_FILE
from manager import ProductManager
from storage import ProductStorage
from ui import ProductApp


def main(page: ft.Page) -> None:
    storage = ProductStorage(PRODUCTS_FILE)
    manager = ProductManager(storage)
    ProductApp(page, manager)


if __name__ == "__main__":
    ft.run(main)

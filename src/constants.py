from pathlib import Path

APP_TITLE = "Менеджер продуктов"
PRODUCTS_FILE = Path(__file__).with_name("products.json")

PRODUCT_TYPE_REGULAR = "regular"
PRODUCT_TYPE_PERISHABLE = "perishable"

TYPE_REGULAR_TITLE = "Обычный"
TYPE_PERISHABLE_TITLE = "Скоропортящийся"

STATE_UNKNOWN = "Состояние не определено"
STATE_NOT_TRACKED = "Срок годности не отслеживается"
STATE_OK = "В норме"
STATE_SOON = "Скоро испортится"
STATE_EXPIRED = "Просрочен"

EXPIRATION_WARNING_DAYS = 3
DATE_FORMAT_DISPLAY = "%d-%m-%Y"

FILTER_ALL = "all"
FILTER_SOON = "soon"
FILTER_EXPIRED = "expired"

FILTER_ALL_TITLE = "Все"
FILTER_SOON_TITLE = "Скоро испортятся"
FILTER_EXPIRED_TITLE = "Просроченные"

EMPTY_LIST_MESSAGE = "Продуктов пока нет"
NAME_REQUIRED_MESSAGE = "Введите название продукта"
QUANTITY_INVALID_MESSAGE = "Количество должно быть целым числом больше нуля"
EXPIRATION_REQUIRED_MESSAGE = "Укажите срок годности"
EXPIRATION_INVALID_MESSAGE = "Некорректная дата. Используйте формат ДД-ММ-ГГГГ"

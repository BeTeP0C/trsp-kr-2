"""Задание 10.1 — Эндпоинты, демонстрирующие пользовательские исключения."""

from fastapi import APIRouter

from app.exceptions import CustomExceptionA, CustomExceptionB

router = APIRouter(prefix="/errors", tags=["Custom Errors (10.1)"])

items_db: dict[int, dict] = {
    1: {"id": 1, "name": "Item A", "stock": 5},
    2: {"id": 2, "name": "Item B", "stock": 0},
}


@router.get("/items/{item_id}")
def get_item(item_id: int):
    """Возвращает элемент по ID. Бросает CustomExceptionB, если не найден."""
    if item_id not in items_db:
        raise CustomExceptionB(detail=f"Item with id={item_id} not found")
    return items_db[item_id]


@router.post("/items/{item_id}/purchase")
def purchase_item(item_id: int, quantity: int = 1):
    """
    Покупка товара. Бросает CustomExceptionB если товар не найден,
    CustomExceptionA если недостаточно запаса.
    """
    if item_id not in items_db:
        raise CustomExceptionB(detail=f"Item with id={item_id} not found")

    item = items_db[item_id]
    if item["stock"] < quantity:
        raise CustomExceptionA(
            detail=f"Not enough stock for '{item['name']}': "
                   f"requested {quantity}, available {item['stock']}",
        )

    item["stock"] -= quantity
    return {"message": f"Purchased {quantity} x {item['name']}", "remaining_stock": item["stock"]}

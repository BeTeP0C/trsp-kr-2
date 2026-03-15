"""Задание 3.2 - GET /product/{product_id}  и  GET /products/search."""

from typing import Optional

from fastapi import APIRouter

from app.services.product import (
    get_product_by_id,
    search_products as search_products_svc,
)

router = APIRouter(tags=["Products"])


@router.get("/product/{product_id}")
def get_product(product_id: int):
    """Возвращает товар по его идентификатору."""
    return get_product_by_id(product_id)


@router.get("/products/search")
def search_products(
    keyword: str,
    category: Optional[str] = None,
    limit: int = 10,
):
    """Поиск товаров по ключевому слову с фильтрацией по категории."""
    return search_products_svc(keyword, category, limit)

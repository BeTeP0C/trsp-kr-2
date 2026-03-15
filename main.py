"""
TRSP KR-2 — FastAPI application
Задания 3.1, 3.2, 5.1–5.5
"""

from fastapi import FastAPI

from app.routers import users, products, auth, headers

app = FastAPI(title="TRSP KR-2")

app.include_router(users.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(headers.router)

"""
TRSP KR-3 — FastAPI application
Задания 3.1, 3.2, 5.1–5.5, 6.1–6.5, 7.1, 8.1–8.2
"""

import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

from app.config import settings
from app.database import create_tables
from app.routers import users, products, auth, headers
from app.routers import basic_auth, jwt_auth, rbac, db_users, todos

# ---------- Задание 6.3: DEV/PROD docs ----------

if settings.mode not in ("DEV", "PROD"):
    raise ValueError(f"Invalid MODE='{settings.mode}'. Allowed: DEV, PROD")

app = FastAPI(
    title="TRSP KR-3",
    docs_url=None,
    redoc_url=None,
    openapi_url=None if settings.mode == "PROD" else "/openapi.json",
)

# Rate-limiter setup (slowapi) — берём limiter из jwt_auth
app.state.limiter = jwt_auth.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------- Startup: создание таблиц SQLite ----------

@app.on_event("startup")
def on_startup():
    create_tables()

# ---------- Существующие роутеры (KR-2) ----------

app.include_router(users.router)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(headers.router)

# ---------- Новые роутеры (KR-3) ----------

app.include_router(basic_auth.router)
app.include_router(jwt_auth.router)
app.include_router(rbac.router)
app.include_router(db_users.router)
app.include_router(todos.router)

# ---------- Задание 6.3: защита документации ----------

if settings.mode == "DEV":
    docs_security = HTTPBasic(auto_error=False)

    def verify_docs_credentials(
        credentials: HTTPBasicCredentials | None = Depends(docs_security),
    ):
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credentials required",
                headers={"WWW-Authenticate": "Basic"},
            )
        correct_user = secrets.compare_digest(
            credentials.username, settings.docs_user,
        )
        correct_pass = secrets.compare_digest(
            credentials.password, settings.docs_password,
        )
        if not (correct_user and correct_pass):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )

    @app.get("/docs", include_in_schema=False)
    def custom_docs(
        _: None = Depends(verify_docs_credentials),
    ):
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=app.title + " — Docs",
        )

elif settings.mode == "PROD":
    @app.get("/docs", include_in_schema=False)
    def docs_not_found():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Not Found"},
        )

    @app.get("/redoc", include_in_schema=False)
    def redoc_not_found():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Not Found"},
        )

    @app.get("/openapi.json", include_in_schema=False)
    def openapi_not_found():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Not Found"},
        )

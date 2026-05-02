"""
TRSP KR-3 / KR-4 — FastAPI application
Задания 3.1, 3.2, 5.1–5.5, 6.1–6.5, 7.1, 8.1–8.2, 9.1, 10.1–10.2, 11.1–11.2
"""

import secrets

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import create_tables
from app.exceptions import (
    CustomExceptionA,
    CustomExceptionB,
    handle_custom_exception_a,
    handle_custom_exception_b,
)
from app.routers import users, products, auth, headers
from app.routers import basic_auth, jwt_auth, rbac, db_users, todos
from app.routers import errors_demo, validation_demo, users_crud

# ---------- Задание 6.3: DEV/PROD docs ----------

if settings.mode not in ("DEV", "PROD"):
    raise ValueError(f"Invalid MODE='{settings.mode}'. Allowed: DEV, PROD")

app = FastAPI(
    title="TRSP KR-3/KR-4",
    docs_url=None,
    redoc_url=None,
    openapi_url=None if settings.mode == "PROD" else "/openapi.json",
)

# ---------- Exception handlers (10.1, 10.2) ----------

app.add_exception_handler(CustomExceptionA, handle_custom_exception_a)
app.add_exception_handler(CustomExceptionB, handle_custom_exception_b)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in err["loc"]),
            "message": err["msg"],
            "type": err["type"],
        })
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": errors},
    )


# Rate-limiter setup (slowapi)
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

# ---------- Роутеры KR-3 ----------

app.include_router(basic_auth.router)
app.include_router(jwt_auth.router)
app.include_router(rbac.router)
app.include_router(db_users.router)
app.include_router(todos.router)

# ---------- Роутеры KR-4 ----------

app.include_router(errors_demo.router)
app.include_router(validation_demo.router)
app.include_router(users_crud.router)

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

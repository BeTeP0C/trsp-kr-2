"""SQLAlchemy-модель Product (задание 9.1)."""

from sqlalchemy import Column, Integer, String, Float

from app.db_sqlalchemy import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    count = Column(Integer, nullable=False, default=0)
    description = Column(String, nullable=False, server_default="")

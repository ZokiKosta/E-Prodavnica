from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    category = Column(String(40), nullable=False)
    image_url = Column(String(500), nullable=False)
    price = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    ai_description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    stock = Column(Integer, default=0, nullable=False)

# class Carts(Base):
#     __tablename__ = "carts"
#
#     id = Column(Integer, primary_key=True)
#     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
#
# class CartItem(Base):
#     __tablename__ = "cart_items"
#
#     id = Column(Integer, primary_key=True)
#     cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
#     product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
#     quantity = Column(Integer, nullable=False, default=1)
#
#     product = relationship("Product")
#
# class Order(Base):
#     __tablename__ = "orders"
#
#     id = Column(Integer, primary_key=True)
#     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
#     status = Column(String(20), default="pending", nullable=False)
#     total_price = Column(Integer, nullable=False, default=0)


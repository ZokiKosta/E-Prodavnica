from datetime import datetime

import bcrypt
import pytz
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

skopje_tz = pytz.timezone("Europe/Skopje")

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

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(120), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(300), nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    verification_code = Column(String(120), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password.encode())

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    action = Column(String(255), nullable=False)
    user_id = Column(Integer)
    username = Column(String(120))
    timestamp = Column(DateTime, default=lambda: datetime.now(skopje_tz))

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    status = Column(String, default="pending")
    # pending, processing, shipped, delivered, cancelled

    user = relationship("User", backref="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    quantity = Column(Integer)
    price = Column(Integer)  # price at purchase time

    order = relationship("Order", back_populates="items")
    product = relationship("Product")

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


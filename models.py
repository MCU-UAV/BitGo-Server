from sqlalchemy import Column, Integer, String, Text, DECIMAL, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from database import Base
import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hashed = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    products = relationship('Product', back_populates='seller')  # 用户发布的商品（作为卖家）
    reviews = relationship('Review', back_populates='user')

    orders = relationship('Order', back_populates='buyer')  # 用户作为买家的订单
    sold_orders = relationship('Order', back_populates='seller')  # 用户作为卖家的订单


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    seller_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))

    seller = relationship('User', back_populates='products')
    category = relationship('Category', back_populates='products')
    images = relationship('ProductImage', back_populates='product')
    reviews = relationship('Review', back_populates='product')


class ProductImage(Base):
    __tablename__ = 'product_images'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    image_url = Column(String(255), nullable=False)

    product = relationship('Product', back_populates='images')


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)

    products = relationship('Product', back_populates='category')


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    buyer_id = Column(Integer, ForeignKey('users.id'))  # 买家 ID
    order_date = Column(DateTime, nullable=False)
    status = Column(Enum('pending', 'shipped', 'completed', 'canceled', name='order_status'), default='pending')
    total_amount = Column(DECIMAL(10, 2), nullable=False)

    # 收货信息字段
    recipient_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255))  # 可选字段

    buyer = relationship('User', back_populates='orders', overlaps="sold_orders")  # 买家
    seller = relationship('User', back_populates='sold_orders', overlaps="orders")  # 卖家


class SoldProduct(Base):
    __tablename__ = 'sold_products'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    seller_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    order_id = Column(Integer, ForeignKey('orders.id'))
    sold_date = Column(DateTime, nullable=False)
    quantity = Column(Integer, nullable=False)

    seller = relationship('User')
    product = relationship('Product')
    order = relationship('Order')  # 通过订单 ID 查询售出商品


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    rating = Column(Integer, nullable=False)  # Assuming a rating scale of 1-5
    comment = Column(Text)
    review_date = Column(DateTime, default=datetime.datetime.utcnow)

    product = relationship('Product', back_populates='reviews')
    user = relationship('User', back_populates='reviews')

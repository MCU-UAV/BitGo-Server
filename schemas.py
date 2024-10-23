from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


# 用户相关模式
class UserPost(BaseModel):
	username: str
	password: str


class UserCreate(BaseModel):
	username: str
	password_hashed: str


class User(BaseModel):
	id: int
	username: str
	password_hashed: str
	created_at: datetime

	class Config:
		from_attributes = True


# 产品相关模式
class ProductCreate(BaseModel):
	name: str
	description: Optional[str] = None
	price: float
	stock: int
	seller_id: int
	category_id: int
	image_urls: List[str]

class Product(BaseModel):
	id: int
	name: str
	description: Optional[str] = None
	price: float
	stock: int
	seller_id: int
	category_id: int
	class Config:
		from_attributes = True


# 定义订单状态的枚举类型
class OrderStatusEnum(str, Enum):
	pending = 'pending'
	shipped = 'shipped'
	completed = 'completed'
	canceled = 'canceled'


# 订单创建模型
class OrderCreate(BaseModel):
	buyer_id: int
	order_date: datetime
	total_amount: float

	# 收货信息字段
	recipient_name: str
	phone: str
	address_line1: str
	address_line2: Optional[str] = None


# 完整的订单模型
class Order(BaseModel):
	id: int
	buyer_id: int
	order_date: datetime
	status: OrderStatusEnum  # 使用枚举类型
	total_amount: float

	# 收货信息字段
	recipient_name: str
	phone: str
	address_line1: str
	address_line2: Optional[str] = None

	class Config:
		from_attributes = True


# 评论相关模式
class CommentCreate(BaseModel):
	product_id: int
	user_id: int
	rating: int
	comment: Optional[str] = None


class Comment(BaseModel):
	id: int
	product_id: int
	user_id: int
	rating: int
	comment: Optional[str] = None
	review_date: datetime

	class Config:
		from_attributes = True


# 产品图片模式
class ProductImageCreate(BaseModel):
	product_id: int
	image_url: str


class ProductImage(BaseModel):
	id: int
	product_id: int
	image_url: str

	class Config:
		from_attributes = True


# 分类相关模式
class CategoryCreate(BaseModel):
	name: str


class Category(BaseModel):
	id: int
	name: str

	class Config:
		from_attributes = True


# 购物车相关模式
class CartCreate(BaseModel):
	user_id: int


class Cart(BaseModel):
	id: int
	user_id: int
	created_at: datetime

	class Config:
		from_attributes = True


# 购物车项相关模式
class CartItemCreate(BaseModel):
	cart_id: int
	product_id: int
	quantity: int


class CartItem(BaseModel):
	id: int
	cart_id: int
	product_id: int
	quantity: int

	class Config:
		from_attributes = True


# 令牌相关模式
class Token(BaseModel):
	access_token: str
	token_type: str

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime
import models
import random
import schemas
from sqlalchemy import or_, func


# 用户相关操作
def get_user(db: Session, username: str):
	user = db.query(models.User).filter(models.User.username == username).first()
	return user


def create_user(db: Session, user: schemas.UserCreate):
	db_user = models.User(**user.dict())
	db.add(db_user)
	try:
		db.commit()
		db.refresh(db_user)
	except IntegrityError:
		db.rollback()
		raise HTTPException(status_code=400, detail="Username already registered")
	return db_user


def get_all_users(db: Session, skip: int = 0, limit: int = 10):
	return db.query(models.User).offset(skip).limit(limit).all()


# 产品相关操作
def get_product(db: Session, product_id: int):
	product = db.query(models.Product).filter(models.Product.id == product_id).first()
	if not product:
		raise HTTPException(status_code=404, detail="Product not found")
	return product


def create_product(db: Session, product: schemas.ProductCreate):
	# 创建产品本身
	db_product = models.Product(
		name=product.name,
		description=product.description,
		price=product.price,
		stock=product.stock,
		seller_id=product.seller_id,
		category_id=product.category_id
	)
	db.add(db_product)
	db.commit()
	db.refresh(db_product)

	# 保存多个图片 URL 到 ProductImage
	for image_url in product.image_urls:
		db_image = models.ProductImage(product_id=db_product.id, image_url=image_url)
		db.add(db_image)

	db.commit()
	return db_product


# 根据ID获取单个商品
def get_product_by_id(db: Session, product_id: int):
	return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_product_images_by_product_id(db: Session, product_id: int):
	return db.query(models.ProductImage).filter(models.ProductImage.product_id == product_id).all()


def get_products_by_seller(db: Session, seller_id: int):
	return db.query(models.Product).filter(models.Product.seller_id == seller_id).all()


def get_category_name_by_id(db: Session, category_id: int):
	return db.query(models.Category).filter(models.Category.id == category_id).first()


# 订单相关操作
def create_order(db: Session, order: schemas.OrderCreate):
	db_order = models.Order(**order.dict())
	db.add(db_order)
	db.commit()
	db.refresh(db_order)
	return db_order


def get_orders_by_user(db: Session, user_id: int):
	return db.query(models.Order).filter(models.Order.buyer_id == user_id).all()  # 修正字段名称


def get_order(db: Session, order_id: int):
	order = db.query(models.Order).filter(models.Order.id == order_id).first()
	if not order:
		raise HTTPException(status_code=404, detail="Order not found")
	return order


# 评论相关操作
def create_comment(db: Session, comment: schemas.CommentCreate):
	db_comment = models.Review(**comment.dict())  # 确保使用正确的模型
	db.add(db_comment)
	db.commit()
	db.refresh(db_comment)
	return db_comment


def get_comments_by_product(db: Session, product_id: int):
	return db.query(models.Review).filter(models.Review.product_id == product_id).all()


def get_comments_by_user(db: Session, user_id: int):
	return db.query(models.Review).filter(models.Review.user_id == user_id).all()


# 额外的帮助函数
def get_product_images(db: Session, product_id: int):
	return db.query(models.ProductImage).filter(models.ProductImage.product_id == product_id).all()


def add_product_image(db: Session, product_id: int, image_url: str):
	db_image = models.ProductImage(product_id=product_id, image_url=image_url)
	db.add(db_image)
	db.commit()
	db.refresh(db_image)
	return db_image


def create_order(db: Session, order_data: schemas.OrderCreate, buyer_id: int):
	total_amount = 0

	# 获取订单中的产品信息
	for item in order_data.products:
		product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
		if not product:
			raise HTTPException(status_code=404, detail=f"产品 ID {item.product_id} 未找到")

		# 检查库存是否足够
		if product.stock < item.quantity:
			raise HTTPException(status_code=400, detail=f"产品 ID {item.product_id} 库存不足")

		total_amount += float(product.price) * item.quantity
		product.stock -= item.quantity  # 更新库存

	# 创建新订单
	new_order = models.Order(
		buyer_id=buyer_id,
		order_date=datetime.utcnow(),
		status='pending',
		total_amount=total_amount,
		recipient_name=order_data.receipt_info.recipient_name,
		phone=order_data.receipt_info.phone,
		address_line1=order_data.receipt_info.address_line1,
		address_line2=order_data.receipt_info.address_line2
	)

	db.add(new_order)
	db.flush()  # 提前获取 new_order 的 ID

	# 记录已售出的产品
	for item in order_data.products:
		product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
		sold_product = models.SoldProduct(
			seller_id=product.seller_id,
			buyer_id = buyer_id,
			product_id=item.product_id,
			order_id=new_order.id,
			sold_date=datetime.utcnow(),
			quantity=item.quantity
		)
		db.add(sold_product)

	db.commit()
	db.refresh(new_order)

	return new_order


def get_order_details(db: Session, order_id: int):
	"""
    获取指定订单的详细信息，包括订单的基本信息和产品详情
    """
	order = db.query(models.Order).filter(models.Order.id == order_id).first()
	if not order:
		raise HTTPException(status_code=404, detail=f"订单 ID {order_id} 未找到")

	# 获取订单中的已售出产品
	sold_products = db.query(models.SoldProduct).filter(models.SoldProduct.order_id == order_id).all()

	# 构造返回的订单详情
	return {
		"id": order.id,
		"buyer_id": order.buyer_id,
		"order_date": order.order_date,
		"status": order.status,
		"total_amount": order.total_amount,
		"recipient_name": order.recipient_name,
		"phone": order.phone,
		"address_line1": order.address_line1,
		"address_line2": order.address_line2,
		"products": [
			{

				"product_id": sold.product_id,
				"quantity": sold.quantity,
				"sold_date": sold.sold_date,
				"seller_id": sold.seller_id,
			}
			for sold in sold_products
		]
	}


def get_products_by_seller(db: Session, seller_id: int):
	"""
    获取卖家发布的商品列表及对应的图片URL
    """
	products = db.query(models.Product).filter(models.Product.seller_id == seller_id).all()

	# 返回商品的详细信息，包括每件商品的图片URL
	result = []
	for product in products:
		product_data = {
			"id": product.id,
			"name": product.name,
			"description": product.description,
			"price": product.price,
			"stock": product.stock,
			"seller_id": product.seller_id,
			"category_id": product.category_id,
			"image_urls": [image.image_url for image in product.images]  # 获取商品的所有图片URL
		}
		result.append(product_data)

	return result


def update_order_status(db: Session, order_id: int, new_status: str):
	"""
    更新订单状态
    :param db: 数据库会话
    :param order_id: 订单 ID
    :param new_status: 新的订单状态
    :return: 更新后的订单
    """
	order = db.query(models.Order).filter(models.Order.id == order_id).first()

	if not order:
		raise HTTPException(status_code=404, detail=f"订单 ID {order_id} 不存在")

	# 更新状态
	order.status = new_status
	db.commit()
	db.refresh(order)

	return order


def get_user_orders(db: Session, user_id: int):
	"""
    获取用户作为买家和卖家的订单号
    :param db: 数据库会话
    :param user_id: 用户ID
    :return: 包含买家和卖家订单号的字典
    """
	# 查询作为买家的订单号
	buyer_orders = db.query(models.Order.id).filter(models.Order.buyer_id == user_id).all()
	# 查询作为卖家的订单号
	seller_orders = db.query(models.SoldProduct.order_id).filter(models.SoldProduct.seller_id == user_id).distinct().all()
	# seller_orders = db.query(models.Order.id).filter(models.Order.seller_id == user_id).all()

	# 将结果整理为简单的列表格式
	result = {
		"buyer_orders": [order.id for order in buyer_orders],
	    "seller_orders": [order[0] for order in seller_orders]
	}
	return result


def create_review(db: Session, review_data: schemas.ReviewCreate, user_id: int, product_id: int):
	# 检查商品是否存在
	product = db.query(models.Product).filter(models.Product.id == product_id).first()
	if not product:
		raise HTTPException(status_code=404, detail="商品未找到")

	# 创建新评论
	new_review = models.Review(
		user_id=user_id,
		product_id=product_id,
		review=review_data.review,
		rating=review_data.rating
	)

	db.add(new_review)
	db.commit()
	db.refresh(new_review)

	return new_review


def get_reviews_by_product_id(db: Session, product_id: int):
	"""
    根据 product_id 获取所有评论
    """
	return db.query(models.Review).filter(models.Review.product_id == product_id).all()


def get_all_categories(db: Session):
	"""
    获取所有分类的 ID 和名称
    """
	return db.query(models.Category.id, models.Category.name).all()


def get_random_products_by_category(db: Session, category_id: int, limit: int = 5):
	"""
    随机获取某分类下的商品以及多个图片信息
    """
	# 查询该分类下的商品，并预加载商品图片信息
	products_query = db.query(models.Product).filter(models.Product.category_id == category_id).options(
		joinedload(models.Product.images)
	)

	# 获取商品总数
	total_products = products_query.count()
	if total_products == 0:
		return []  # 如果没有商品，返回空列表

	# 随机选择商品（通过数据库实现随机排序，避免全部加载到内存）
	random_products = products_query.order_by(func.random()).limit(limit).all()

	# 构造结果数据
	result = [
		{
			"id": product.id,
			"name": product.name,
			"description": product.description,
			"price": float(product.price),
			"stock": product.stock,
			"seller_id": product.seller_id,
			"category_id": product.category_id,
			"image_urls": [image.image_url for image in product.images],  # 获取图片 URL
		}
		for product in random_products
	]

	return result


def get_random_products(db: Session, limit: int = 5):
	"""
    随机返回数个商品及其图片信息
    """
	# 查询所有商品，并预加载商品图片信息
	products_query = db.query(models.Product).options(joinedload(models.Product.images))

	# 获取商品总数
	total_products = products_query.count()
	if total_products == 0:
		return []  # 如果没有商品，返回空列表

	# 随机选择商品（通过数据库实现随机排序，避免加载所有商品到内存）
	random_products = products_query.order_by(func.random()).limit(limit).all()

	# 构造结果数据
	result = [
		{
			"id": product.id,
			"name": product.name,
			"description": product.description,
			"price": float(product.price),
			"stock": product.stock,
			"seller_id": product.seller_id,
			"category_id": product.category_id,
			"image_urls": [image.image_url for image in product.images],  # 获取图片 URL
		}
		for product in random_products
	]

	return result


def search_products(db: Session, keyword: str, limit: int = 10):
	"""
    模糊查找商品
    """
	query = db.query(models.Product).filter(
		or_(
			models.Product.name.ilike(f"%{keyword}%"),  # 商品名称包含关键字
			models.Product.description.ilike(f"%{keyword}%")  # 商品描述包含关键字
		)
	).limit(limit)

	products = query.all()

	# 构造返回数据，包括商品图片
	result = []
	for product in products:
		product_data = {
			"id": product.id,
			"name": product.name,
			"description": product.description,
			"price": float(product.price),
			"stock": product.stock,
			"seller_id": product.seller_id,
			"category_id": product.category_id,
			"image_urls": [image.image_url for image in product.images]  # 获取图片 URL
		}
		result.append(product_data)

	return result

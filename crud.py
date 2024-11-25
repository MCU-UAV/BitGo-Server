from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime
import models
import schemas


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
            product_id=item.product_id,
            order_id=new_order.id,
            sold_date=datetime.utcnow(),
            quantity=item.quantity
        )
        db.add(sold_product)

    db.commit()
    db.refresh(new_order)

    return new_order


def create_review(db: Session, review_data: schemas.ReviewCreate, user_id: int, product_id: int):
    # 检查商品是否存在
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品未找到")

    # 创建新评论
    new_review =models.Review(
        user_id=user_id,
        product_id=product_id,
        content=review_data.content,
        rating=review_data.rating
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review
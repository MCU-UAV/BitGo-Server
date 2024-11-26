from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
import crud, models, schemas, auth
from database import get_db, engine

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以指定具体的源，例如 ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册新用户
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserPost, db: Session = Depends(get_db)):
    # 检查用户名是否已经存在
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # 哈希处理密码
    hashed_password = auth.hash_password(user.password)

    # 创建一个新的用户对象，只有哈希密码
    user_with_hashed_password = schemas.UserCreate(
        username=user.username,
        password_hashed=hashed_password  # 使用哈希密码
    )

    # 保存用户
    return crud.create_user(db=db, user=user_with_hashed_password)


# 登录并获取 JWT token
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


# 获取当前用户信息
@app.get("/users/me")
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return {"username": current_user.username, "user_id": current_user.id}


# 测试登录保护的数据
@app.get("/protected")
async def read_protected_data(current_user: schemas.User = Depends(auth.get_current_user)):
    return {"message": "这是受保护的数据", "user": current_user.username}


@app.post("/product/create")
def create_new_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    try:
        # 调用 CRUD 函数创建产品
        db_product = crud.create_product(db, product)
        return {
            "success": True,
            "product": db_product.name,
            "message": "产品发布成功"
        }
    except Exception as e:
        # 捕获异常并返回错误信息
        raise HTTPException(status_code=500, detail=f"产品发布失败: {str(e)}")


# 获取商品详情
@app.get("/products/{product_id}/detail", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# 获取商品图片
@app.get("/product/{product_id}/images", response_model=List[schemas.ProductImage])
def read_product(product_id: int, db: Session = Depends(get_db)):
    product_images = crud.get_product_images_by_product_id(db, product_id)
    if not product_images:
        raise HTTPException(status_code=404, detail="Product images not found")
    return product_images


# 获取商品分类名
@app.get("/categories/{category_id}/name")
async def read_category_name(category_id: int, db: Session = Depends(get_db)):
    category = crud.get_category_name_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


# 创建订单
@app.post("/order/create", response_model=schemas.OrderResponse)
async def create_order(
        order_data: schemas.OrderCreate,  # 通过请求体传递 OrderCreate 类型的数据
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(auth.get_current_user)
):
    try:
        # 调用 crud.create_order 创建订单
        new_order = crud.create_order(db=db, order_data=order_data, buyer_id=current_user.id)

        # 构建订单响应模型
        order_response = schemas.OrderResponse(
            id=new_order.id,
            buyer_id=new_order.buyer_id,
            order_date=new_order.order_date.isoformat(),  # 格式化日期为 ISO 8601 字符串
            status=new_order.status,
            total_amount=new_order.total_amount,
            products=[
                schemas.ProductOrder(product_id=item.product_id, quantity=item.quantity)
                for item in order_data.products
            ],
            receipt_info=schemas.ReceiptInfo(
                recipient_name=order_data.receipt_info.recipient_name,
                phone=order_data.receipt_info.phone,
                address_line1=order_data.receipt_info.address_line1,
                address_line2=order_data.receipt_info.address_line2
            )
        )

        return order_response  # 返回订单响应模型

    except HTTPException as e:
        print(e)
        # 捕获 HTTP 异常并返回错误信息
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        # 捕获其他异常并返回通用错误信息
        raise HTTPException(status_code=500, detail=f"订单创建失败: {str(e)}")


# 得到用户的所有订单
@app.get("/user/orders")
async def read_user_orders(current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    orders = crud.get_user_orders(db, current_user.id)
    if not orders["buyer_orders"] and not orders["seller_orders"]:
        raise HTTPException(status_code=404, detail="未找到相关订单")
    return orders

# 获取订单详情
@app.get("/orders/{order_id}")
async def read_order_details(order_id: int, db: Session = Depends(get_db)):
    """
    获取订单的详细信息
    """
    order_details = crud.get_order_details(db, order_id)
    return order_details

#获取该用户发布的商品
@app.get("/products/seller")
async def get_products_for_seller(current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """
    获取某卖家发布的商品列表
    """
    products = crud.get_products_by_seller(db, current_user.id)

    if not products:
        raise HTTPException(status_code=404, detail="没有找到该卖家的商品")

    return products

# 对某一商品进行评论
@app.post("/product/{product_id}/review", response_model=schemas.ReviewResponse)
async def post_review(
        product_id: int,
        review_data: schemas.ReviewCreate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(auth.get_current_user)
):
    try:
        # 用户对商品进行评论
        new_review = crud.create_review(db=db, review_data=review_data, user_id=current_user.id, product_id=product_id)
        return new_review
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="评论创建失败")


# 查看某件商品的所有评论
@app.get("/product/{product_id}/reviews", response_model=List[schemas.ReviewResponse])
async def get_reviews(product_id: int, db: Session = Depends(get_db)):
    """
       获取某个商品的所有评论
       """
    reviews = crud.get_reviews_by_product_id(db, product_id)
    return reviews


# 获取所有分类ID和分类名
@app.get("/categories", response_model=List[schemas.Category])
def get_categories(db: Session = Depends(get_db)):
    """
    获取所有分类的 ID 和名称
    """
    categories = crud.get_all_categories(db)
    # 转换为字典列表，以满足 Pydantic 的序列化需求
    return [{"id": category[0], "name": category[1]} for category in categories]


@app.get("/categories/{category_id}/products", response_model=List[schemas.Product])
def get_random_products(category_id: int, limit: int = 5, db: Session = Depends(get_db)):
    """
    随机获取某分类下的商品及其多个图片URL
    """
    products = crud.get_random_products_by_category(db, category_id, limit)
    if not products:
        raise HTTPException(status_code=404, detail="该分类下没有商品")
    return products

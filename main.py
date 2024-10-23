from fastapi import FastAPI, Depends, HTTPException, status
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
@app.post("/register/", response_model=schemas.User)
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
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
@app.get("/products/{product_id}/image", response_model=List[schemas.ProductImage])
def read_product(product_id: int, db: Session = Depends(get_db)):
	product_images = crud.get_product_images_by_product_id(db, product_id)
	if not product_images:
		raise HTTPException(status_code=404, detail="Product images not found")
	return product_images

#获取商品分类名
@app.get("/categories/{category_id}/name")
async def read_category_name(category_id: int, db: Session = Depends(get_db)):
	category = crud.get_category_name_by_id(db, category_id)
	if not category:
		raise HTTPException(status_code=404, detail="Category not found")
	return category
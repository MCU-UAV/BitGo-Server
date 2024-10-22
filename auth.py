from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import crud
import schemas
from database import get_db

# 秘钥和算法设置
SECRET_KEY = "test123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 设置密码哈希算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 令牌端点
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 验证密码是否正确
def verify_password(plain_password: str, password_hashed: str) -> bool:
	return pwd_context.verify(plain_password, password_hashed)


# 哈希密码函数
def hash_password(password: str) -> str:
	return pwd_context.hash(password)


# 用户身份验证
def authenticate_user(db: Session, username: str, password: str):
	user = crud.get_user(db, username)  # 从数据库获取用户信息
	if not user:
		return False
	if not verify_password(password, user.password_hashed):  # 验证密码是否匹配
		return False
	return user


# 创建 JWT 访问令牌
def create_access_token(data: dict, expires_delta: timedelta = None):
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.utcnow() + expires_delta
	else:
		expire = datetime.utcnow() + timedelta(minutes=15)
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt


# 获取当前用户信息
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		username: str = payload.get("sub")
		if username is None:
			raise credentials_exception
	except JWTError:
		raise credentials_exception
	user = crud.get_user(db, username=username)
	if user is None:
		raise credentials_exception
	return user

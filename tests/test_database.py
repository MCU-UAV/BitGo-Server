import pytest
from sqlalchemy.orm import Session
from database import get_db, engine
from models import User, Product, CartItem


def test_db_connection():
    # 使用 get_db 函数创建一个数据库会话
    db = next(get_db())
    assert db is not None  # 确认数据库连接正常



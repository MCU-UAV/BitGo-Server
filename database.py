from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 更新为你的 MySQL 数据库连接字符串
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://bitgodbadmin:ymDXpYqim2JDBJM7@mysql.sqlpub.com:3306/bitgodb"

engine = engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,           # 最大连接池大小，设置为20（小于30的限制）
    max_overflow=10,        # 允许的额外连接数，防止临时连接高峰
    pool_timeout=30,        # 超时时间，30秒后放弃获取连接
    pool_recycle=1800,      # 回收连接时间（秒），防止长时间连接导致的问题
    pool_pre_ping=True,     # 预检测连接可用性，防止使用无效连接
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

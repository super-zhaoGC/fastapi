"""
数据库链接会话
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_size=True,  # 测试连通性
    pool_recycle=3600,  # 连接池回收时间(秒)
    echo=False,  # 是否打印SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,  # 不自动提交事务
    autoflush=False,  # 不自动刷新会话
    bind=engine,  # 绑定引擎实例
)


def get_db():
    """数据库会话依赖，用于 FastAPI 依赖注入

    每次请求创建一个新的数据库会话，请求结束后自动关闭。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
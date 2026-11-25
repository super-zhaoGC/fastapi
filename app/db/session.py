"""
数据库链接会话
"""
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    pool_size=10,  # 最大连接数大小池
    pool_recycle=3600,  # 连接池回收时间(秒)
    echo=False,  # 是否打印SQL语句
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    # autocommit=False,  # 不自动提交事务
    # autoflush=False,  # 不自动刷新会话
    # bind=engine,  # 绑定引擎实例
    bind=engine,
    class_=AsyncSession,  # 使用异步会话
    expire_on_commit=False,  # 不自动刷新会话
)


async def get_db()-> AsyncGenerator[AsyncSession, Any]:
    """数据库会话依赖，用于 FastAPI 依赖注入

    每次请求创建一个新的数据库会话，请求结束后自动关闭。
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e

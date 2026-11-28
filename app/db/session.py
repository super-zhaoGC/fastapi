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
    # 每条连接建立后先设置会话时区。
    # 原因：本机 MySQL 的 system_time_zone 是 UTC，而 create_time/update_time 用的
    # server_default=func.now() / onupdate=func.now() 都是 MySQL 的 NOW()，
    # 不设置就会把 UTC 写进库，比本地时间(东八区)慢 8 小时。
    connect_args={"init_command": "SET time_zone = '+08:00'"},
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

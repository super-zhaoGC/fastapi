from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有 Model 继承此类"""

    pass


class TimestampMixin:
    """创建时间 / 更新时间

    字段名与数据库表、Pydantic schema 保持一致：create_time / update_time，
    这样 ORM 属性、表列、接口返回三处的名字统一，不会再出现
    “模型有 created_at 但表里叫 create_time” 的错位。
    """

    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )


class BaseModel(Base, TimestampMixin):
    """所有数据表的基类

    注意：这里不再内置 id 字段。本项目各表使用业务主键
    （例如 user 表的 user_id），与数据库表结构和 schema 保持一致。
    如果将来某张表确实需要自增 id，在该模型里单独声明即可。
    """

    __abstract__ = True

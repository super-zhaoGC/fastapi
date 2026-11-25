from app.core.base_model import BaseModel

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

class User(BaseModel):
    """用户模型"""
    __tablename__ = "user"

    # 用户ID(自增主键)
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    # 用户名
    user_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="用户名")
    # 用户性别(0男 1女)
    sex: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="用户性别(0男 1女)")
    # 用户头像
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="用户头像")
    # 密码
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码")

"""
用户服务层
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.model import User
from app.modules.user.schema import UserSchema
from sqlalchemy import select


class UserService:
    # def __init__(self,db: AsyncSession):
    #     self.db = db

    def _to_schema(self,user: User) -> dict:
        """
        将 ORM 用户实体序列化为接口返回的 JSON 字典

        1. 先通过 Pydantic 将 ORM 实体校验并转换为 UserSchema 实例
        2. 再序列化为字典: 按字段别名输出键名(如 userId/createTime)，并将
           create_time 格式化为 "YYYY-MM-DD HH:MM:SS"
        """
        # 1. 将 ORM 实体校验转换为 UserSchema 模型实例
        schema = UserSchema.model_validate(user)
        # 2. 序列化为字典: 使用字段别名作为键名，并应用 create_time 时间格式化
        return schema.model_dump(by_alias=True)

    async def select_user_by_user_name(self,db: AsyncSession, user_name: str) -> dict | None:
        """
        根据用户名查询用户
        """
        statement = select(User).where(User.user_name == user_name)
        result = await db.execute(statement)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return self._to_schema(user)

    async def select_user_by_user_id(self, user_id: int, db: AsyncSession) -> dict | None:
        """
        通过用户ID查询用户信息
        
        参数:
            user_id: 用户ID
            db: 数据库会话
        
        返回:
            用户信息字典，如果不存在则返回None
        """
        user = await db.get(User, user_id)  # 根据用户ID从数据库获取用户实体
        if user is None:  # 判断用户是否存在
            return None  # 不存在则返回None
        return self._to_schema(user)  # 存在则序列化为字典并返回
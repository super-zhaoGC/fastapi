"""
用户服务层
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exception_handler import ServiceError
from app.modules.user.model import User, UserRole
from app.modules.user.schema import UserSchema
from sqlalchemy import select

from app.utils.security_utils import encrypt_password


class UserService:
    # def __init__(self,db: AsyncSession):
    #     self.db = db

    def _to_schema(self, user: User) -> dict:
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

    async def select_user_by_user_name(self, db: AsyncSession, user_name: str) -> dict | None:
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

    async def register_user(self, register_data: dict, db: AsyncSession) -> int:
        """
        注册新用户
        
        Args:
            register_data: 包含注册信息的字典
                - user_name: 用户名，用于登录系统
                - password: 密码，将被加密存储
            db: 数据库会话对象，用于执行数据库操作
        
        Returns:
            int: 注册成功返回1
        
        Raises:
            ServiceError: 当用户名已存在时抛出
        """
        # 第一步：校验用户名是否已被注册
        # 从请求数据中提取用户名，若为空则默认为空字符串
        user_name = register_data.get("userName") or ""
        # 调用用户查询方法，检查该用户名是否已存在
        existing = await self.select_user_by_user_name(db, user_name)
        if existing is not None:
            # 用户名已存在，抛出业务异常提示用户
            raise ServiceError("用户名已存在")

        # 第二步：创建新用户并分配默认角色
        # 使用加密函数对密码进行加密处理，确保密码安全存储
        user = User(
            user_name=user_name,
            password=encrypt_password(register_data.get("password") or ""),
        )
        # 将新用户对象添加到数据库会话，此时还未提交到数据库
        db.add(user)
        # 执行flush操作，将用户信息刷新到数据库，获取用户ID等自增字段
        await db.flush()

        # 导入角色ID常量，为新用户分配默认用户角色
        from app.utils.constants import RoleIdConstants
        # 创建用户角色关联记录，将用户与默认角色进行绑定
        db.add(UserRole(
            user_id=user.user_id,
            role_id=RoleIdConstants.USER_ROLE_ID,
        ))

        # 提交事务，将用户信息和角色关联信息一起持久化到数据库
        await db.commit()
        # 返回1表示注册成功
        return 1

    async def update_user_avatar(self, user_id: int, db: AsyncSession, avatar: str) -> int:
        """
        更新用户头像
        :param self:
        :param user_id: 用户ID
        :param db: 数据库会话对象
        :param avatar: 头像URL
        :return: 更新成功返回1，否则返回0
        """
        user = await db.get(User, user_id)
        if user is None:
            return 0
        user.avatar = avatar
        await db.commit()
        return 1

    async def update_profile(self, user_id: int, user_name: str | None, sex: int | None, db: AsyncSession) -> int:
        """
        更新用户个人信息
        :param user_id: 用户ID
        :param user_name: 用户名
        :param sex: 用户性别
        :param db: 数据库会话对象
        :return: 更新成功返回1，否则返回0
        """
        # 根据用户ID从数据库查询用户对象
        user = await db.get(User, user_id)
        # 若用户不存在，则返回0表示更新失败
        if user is None:
            return 0

        # 仅在提供用户名时更新用户名字段
        if user_name:
            user.user_name = user_name

        # 仅在提供性别值时更新性别字段（注意：sex为0也视为有效值）
        if sex is not None:
            user.sex = sex

        # 提交事务以保存所有更新
        await db.commit()
        return 1
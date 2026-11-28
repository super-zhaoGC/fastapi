from pydantic import BaseModel, ConfigDict, Field, field_serializer
from datetime import datetime

class UserSchema(BaseModel):
    # from_attributes: 允许从任意对象(含 SQLAlchemy ORM 实体)按属性读取，model_validate(User) 才能工作
    # populate_by_name: 字段都声明了 alias(userId/createTime)，Pydantic v2 默认只按 alias 校验，
    #   会把 ORM 实体的 user_id/create_time 当成缺失而静默取默认值 None，必须额外允许按字段名取值
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # 用户ID
    user_id: int | None = Field(default=None, alias="userId")
    # 用户名
    user_name: str | None = Field(default=None, alias="userName")
    # 用户性别
    sex: int | None = None
    # 用户头像
    avatar: str | None = None
    # 密码
    password: str | None = None
    # 创建时间
    create_time: datetime | None = Field(default=None, alias="createTime")

    @field_serializer("create_time")
    def serialize_time(self, value: datetime | None):
        """时间格式化: 返回给前端时统一显示为 xxxx-xx-xx xx:xx:xx"""
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")

class UpdateProfile(BaseModel):
    """
    更新用户个人信息
    """
    model_config = {"populate_by_name": True} # 允许按字段名取值

    user_name:str|None=Field(default=None,alias="userName")
    sex:int|None=None

class UpdatePassword(BaseModel):
    """
    更新用户密码
    """
    model_config = {"populate_by_name": True}

    old_password:str=Field(alias="oldPassword")
    new_password:str=Field(alias="newPassword")
    confirm_password:str=Field(alias="confirmPassword")


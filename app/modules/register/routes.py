from fastapi import APIRouter,Depends
from sqlalchemy import true
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.login.schema import RegisterModel
from app.utils.common import response_error, response_success
from app.modules.user.service import UserService

register_router = APIRouter()
user_service= UserService()

@register_router.post("", tags=["register"],summary="注册用户")
async def register_user(register_data:RegisterModel,db: AsyncSession=Depends(get_db)):
    """
    注册用户
    :param register_data: 注册用户数据
    :param db: 数据库会话
    :return: 注册成功响应
    """
    user_name=register_data.user_name
    password=register_data.password
    if not user_name or not password:
        return response_error(msg="用户名或密码不能为空")

    reg_flag=await user_service.register_user(register_data.model_dump(by_alias=True), db)
    if not reg_flag:
        return response_error(msg="注册失败")
    return response_success(msg="注册成功")



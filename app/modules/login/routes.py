from fastapi import APIRouter, Depends

from app.core import token_service
from app.core.exception_handler import ServiceError
from app.db.session import get_db
from app.schemas.common import response_success
from app.modules.login.schema import LoginModel, LoginResponse
from app.modules.user.service import UserService
from app.utils.security_utils import check_password
from sqlalchemy.ext.asyncio import AsyncSession

login_router = APIRouter()  # 创建登录路由实例
user_service = UserService()  # 初始化用户服务实例


@login_router.post("/", response_model=LoginResponse)  # 定义登录接口，POST方法
async def login(login_data: LoginModel, db: AsyncSession = Depends(get_db)):  # 登录函数，接收登录数据和数据库会话
    """
    用户登录接口
    
    参数:
        login_data: 登录请求数据，包含用户名和密码
        db: 数据库会话依赖注入
    
    返回:
        包含JWT token的成功响应
    """
    user_name = (login_data.user_name or "").strip()  # 获取用户名并去除首尾空白
    password = (login_data.password or "").strip()  # 获取密码并去除首尾空白
    if not user_name or not password:  # 判断用户名或密码是否为空
        raise ServiceError("用户名或密码不能为空")  # 抛出服务错误异常

    user = await user_service.select_user_by_user_name(db, user_name)  # 根据用户名查询用户信息
    if user is None:  # 判断用户是否存在
        raise ServiceError("用户名错误")  # 用户不存在，抛出服务错误异常

    if not check_password(password, user.get("password") or ""):  # 验证密码是否正确
        raise ServiceError("密码错误")  # 密码错误，抛出服务错误异常

    login_user = {  # 构建登录用户信息字典
        "userId": user["userId"],  # 用户ID
        "user": {  # 用户详细信息
            "userId": user["userId"],  # 用户ID
            "userName": user["userName"],  # 用户名
            "sex": user["sex"],  # 性别
            "avatar": user["avatar"],  # 头像
            "password": user["password"],  # 密码
        },
    }
    token = token_service.create_token(login_user)  # 创建JWT令牌

    return response_success(token=token)  # 返回包含令牌的的成功响应
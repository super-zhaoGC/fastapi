"""
公共依赖模块
作用: 提供整个项目通用的依赖注入函数
相当于系统的安检员 - 检查每个访客的通行证(token), 验证通过才放行

核心功能:
- 验证用户请求中的 Bearer Token
- 解析并验证 Token 的有效性
- 验证失败时返回 401 未授权错误

使用方式:
在需要验证登录的路由函数参数中使用: Depends(get_current_user)
"""

# FastAPI 核心依赖注入和异常处理
from fastapi import Depends, HTTPException
# HTTP 授权凭证模型和安全方案
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Token 服务 - 负责 Token 的解析、验证等核心逻辑
from app.core import token_service

# ============================================================
# 安全方案配置
# ============================================================
# HTTPBearer: FastAPI 提供的 Bearer Token 安全方案
# 声明成 HTTPBearer 后, FastAPI 会自动写入 openapi.json
# Swagger UI 右上角就会出现 Authorize 按钮, 方便测试
#
# auto_error=False 参数说明:
# - True: 请求头缺少 Authorization 时, 框架层直接返回 401
# - False: 缺少请求头时不在框架层报错, 继续往下走
#   这样我们可以在函数中统一处理, 返回更友好的错误信息"登录已过期"
security = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict:
    """
    获取当前登录用户

    参数:
        credentials: HTTPBearer 依赖注入的凭证对象
                    如果 auto_error=False 且请求头缺失, 则为 None

    返回:
        dict: 登录用户信息字典, 包含用户ID、用户名等

    异常:
        HTTPException: Token 无效或已过期时抛出 401 错误

    处理流程:
        步骤1: 从请求头中提取 token
        步骤2: 解析 token, 获取用户信息
        步骤3: 验证 token 是否过期
        步骤4: 验证通过, 返回用户信息
    """
    # --------------------------------------------------------
    # 步骤1: 从请求头中提取 token
    # --------------------------------------------------------
    # credentials 格式: HTTPAuthorizationCredentials(scheme="Bearer", credentials="xxx")
    # 如果请求头缺失且 auto_error=False, credentials 为 None
    authorization = f"Bearer {credentials.credentials}" if credentials else None

    # token_service.get_token() 负责从 "Bearer xxx" 格式中提取真正的 token 字符串
    token = token_service.get_token(authorization)

    # --------------------------------------------------------
    # 步骤2: 解析 token, 获取用户信息
    # --------------------------------------------------------
    # get_login_user() 会解码 JWT token, 提取用户信息
    # 如果 token 格式错误或被篡改, 可能返回 None
    login_user = token_service.get_login_user(token)
    if login_user is None:
        # Token 解析失败 (格式错误/被篡改/恶意伪造)
        raise HTTPException(status_code=401, detail="登录已过期, 请重新登录")

    # --------------------------------------------------------
    # 步骤3: 验证 token 是否过期
    # --------------------------------------------------------
    # 即使 token 格式正确, 还需要检查是否在有效期内
    # JWT 的 exp 字段记录了过期时间
    if not token_service.verify_token(login_user):
        # Token 已过期
        raise HTTPException(status_code=401, detail="登录已过期, 请重新登录")

    # --------------------------------------------------------
    # 步骤4: 验证通过, 返回用户信息
    # --------------------------------------------------------
    # login_user 字典示例:
    # {
    #     "user_id": 123,
    #     "username": "zhangsan",
    #     "exp": 1699999999  # 过期时间戳
    # }
    return login_user
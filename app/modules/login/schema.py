"""
登陆注册相关的请求模型
"""
from pydantic import BaseModel,Field


class LoginModel(BaseModel):
    # model_config = {"populate_by_name":True}
    user_name: str|None=Field(default=None,alias="userName")
    password: str|None

class LoginResponse(BaseModel):
    """登录成功后的响应模型

    注意: 不能用 LoginModel 充当 response_model —— 那是请求模型(含必填 password),
    接口实际返回 {code, msg, token}, 用请求模型校验响应会因缺少 password 报
    ResponseValidationError(500)。
    """

    code: int = 200
    msg: str = "操作成功"
    token: str

class RegisterModel(BaseModel):
    """注册请求模型"""
    # 开启按字段赋值
    model_config = {"populate_by_name":True}
    user_name: str=Field(alias="userName")
    password: str=Field(min_length=6,max_length=20)
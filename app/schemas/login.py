"""
登陆注册相关的请求模型
"""
from pydantic import BaseModel,Field


class LoginModel(BaseModel):
    # model_config = {"populate_by_name":True}
    user_name: str|None=Field(default=None,alias="userName")
    password: str|None

class RegisterModel(BaseModel):
    user_name: str=Field(alias="userName")
    password: str=Field(min_length=6,max_length=20)
    age:int=Field(default=18,ge=1,le=120)
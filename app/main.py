from fastapi import FastAPI
from app.core.logger import logger
from app.schemas.common import response_success, response_error
from app.schemas.login import LoginModel
# 创建fastapi应用实例
app = FastAPI(title="FastAPI权限系统")


# 定义一个接口
@app.get("/")
def home():
    logger.info("Hello World")
    return {"message": "Hello World"}

@app.get("/testSuccess")
def testSuccess(data="Hello World"):
    return response_success(data=data)


@app.post("/login")
def login(login_data:LoginModel):
    return response_success(data=login_data)
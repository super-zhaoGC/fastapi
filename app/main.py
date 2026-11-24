from fastapi import FastAPI
from app.core.logger import logger
# 创建fastapi应用实例
app = FastAPI(title="FastAPI权限系统")


# 定义一个接口
@app.get("/")
def home():
    logger.info("Hello World")
    return {"message": "Hello World"}

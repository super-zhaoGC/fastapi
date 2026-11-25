from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.core.logger import logger
from app.schemas.common import response_success, response_error
from app.schemas.login import LoginModel
from pathlib import Path
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

# 创建fastapi应用实例
app = FastAPI(title="FastAPI权限系统")


# 跨域配置
# 这个配置就是告诉浏览器: "允许外部网站访问我"
app.add_middleware(
    CORSMiddleware,
    # 1.允许哪些来源访问(正则.*表示允许所有来源)
    # 注意: 要配合下面的credentials=True, 必须用正则方式, 写allow_origins=["*"]是不生效的
    allow_origin_regex=".*",
    # 2.允许携带凭证(如cookies、HTTP认证信息)
    allow_credentials=True,
    # 3.允许哪些HTTP方法(GET POST PUT DELETE等等)
    allow_methods=["*"],
    # 4.允许携带哪些请求头
    allow_headers=["*"],
    # 5.预检请求的缓存时间(秒): 浏览器发送复杂请求前会先发OPTIONS预检请求, 1800秒内不用重复发
    max_age=1800,
)

# 定义一个接口
@app.get("/")
def home():
    logger.info("Hello World")
    return {"message": "Hello World"}


@app.get("/testSuccess")
def testSuccess(data="Hello World"):
    return response_success(data=data)


@app.post("/login")
def login(login_data: LoginModel):
    return response_success(data=login_data)

# 配置文件上传路径
profile_dir = Path(settings.fast_profile)
profile_dir.mkdir(parents=True, exist_ok=True)
app.mount("/profile",StaticFiles(directory="profile_dir"), name="profile")

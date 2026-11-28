from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from starlette.staticfiles import StaticFiles

from loguru import logger
from pathlib import Path
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

from app.core.exception_handler import register_exception_handlers

from app.modules.home.routes import home_router
from app.modules.login.routes import login_router
from app.modules.user.routes import user_router
from app.modules.register.routes import register_router


version="v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期回调(lifespan)

    替代已废弃的 @app.on_event("startup") / @app.on_event("shutdown"):
    yield 之前的代码 = 启动时执行, yield 之后的代码 = 关闭时执行。
    应用实例通过 FastAPI(lifespan=lifespan) 挂载后生效。
    """
    # ---------- 启动 ----------
    banner = (
        "\n------------------------------------------\n"
        "  FastAPI权限系统 启动成功!\n"
        f"  接口文档地址: http://localhost:{settings.server_port}/docs\n"
        f"  后端首页地址: http://localhost:{settings.server_port}/\n"
        "------------------------------------------"
    )
    logger.info(banner)
    yield
    # ---------- 关闭 ----------
    logger.info("FastAPI权限系统 已停止")


# 创建fastapi应用实例
# docs_url/redoc_url 置空: 关闭 FastAPI 自带的文档页(它从 cdn.jsdelivr.net 加载
# swagger-ui 静态资源, 该域名常被重置, 会导致 /docs 白屏), 改由下方自定义路由
# 指向本地 app/static 下的资源, 变成完全离线可用。
app = FastAPI(
    title="FastAPI权限系统",
    version=version,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

# ---------------------------------------------------------------------------
# 修正 OpenAPI 中文件上传字段的 schema（说明见文件末尾）
# ---------------------------------------------------------------------------


# 本地静态资源目录(swagger-ui / redoc 的 js、css)
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    """Swagger UI 文档页(使用本地静态资源, 不依赖外网 CDN)"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def custom_redoc():
    """ReDoc 文档页(同样使用本地静态资源)"""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="/static/redoc/redoc.standalone.js",
    )


# 注册全局异常处理器(ServiceError -> 400 统一JSON, HTTPException -> 统一JSON)
register_exception_handlers(app)

# 注册路由模块
# app.include_router(home_router,prefix=f"/api/{version}/home",tags=["home"])
app.include_router(home_router,prefix=f"/home",tags=["home"])
app.include_router(login_router,prefix=f"/login",tags=["login"])
app.include_router(user_router,prefix=f"/system/user",tags=["user"])
app.include_router(register_router,prefix=f"/register",tags=["register"])



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


# 配置文件上传路径
profile_dir = Path(settings.fast_profile)
profile_dir.mkdir(parents=True, exist_ok=True)
app.mount("/profile",StaticFiles(directory=profile_dir), name="profile")


# ---------------------------------------------------------------------------
# 修正 OpenAPI 中上传文件字段的 schema
#
# 问题: FastAPI 0.141 + Pydantic 2.13 把 UploadFile 描述成
#   {"type": "string", "contentMediaType": "application/octet-stream"}
# 而 /docs 使用的 Swagger UI(5.17) 只认 "format": "binary" 才会渲染「选择文件」按钮;
# 只看到 contentMediaType 时它会渲染成一个普通文本框, 并填上一段随机的二进制
# 示例值(界面上那串看不懂的乱码), 完全没法选文件。
#
# 处理: 首次生成 OpenAPI 后, 给这类字段补上 format: binary, 其余内容不变。
# 必须放在所有 include_router / mount 之后, 否则生成出来的 schema 会漏掉路由。
# ---------------------------------------------------------------------------
_openapi_schema = app.openapi()  # 首次调用会生成并缓存到 app.openapi_schema
for _component in (_openapi_schema.get("components", {}).get("schemas") or {}).values():
    for _prop in (_component.get("properties") or {}).values():
        if _prop.get("contentMediaType") == "application/octet-stream":
            _prop["format"] = "binary"
app.openapi_schema = _openapi_schema

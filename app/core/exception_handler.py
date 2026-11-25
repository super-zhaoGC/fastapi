# FastAPI 相关组件
from fastapi import FastAPI, Request
# 用于返回自定义 JSON 响应的响应类
from fastapi.responses import JSONResponse
# 日志组件
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException


# 统一错误响应 Schema
from app.schemas.common import response_error


class ServiceError(Exception):
    """
    业务异常类

    用于在业务逻辑中抛出非技术性错误, 如参数校验失败、业务规则违反等。
    该异常会被全局异常处理器捕获并转换为 HTTP 400 响应返回给客户端。
    """
    def __init__(self, message: str):
        self.message = message


def register_exception_handlers(app: FastAPI):
    """
    注册全局异常处理器

    将 ServiceError 业务异常绑定到统一的处理函数, 记录错误日志后
    以 HTTP 400 状态码和统一格式的 JSON 响应返回给客户端。

    参数:
        app: FastAPI 应用实例
    """
    # 注册 ServiceError 的专属异常处理器
    @app.exception_handler(ServiceError)
    async def handle_service_error(request: Request, exc: ServiceError):
        # 记录业务异常日志
        logger.error(f"业务异常: {exc.message}")
        # 返回 HTTP 400, 响应体为统一错误格式
        return JSONResponse(content=response_error(msg=exc.message), status_code=400)

    # 注册StarletteHTTPException异常处理器
    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException):  # 处理HTTP异常
        # 返回JSON响应，状态码使用异常的状态码，响应体包含错误码和错误信息
        return JSONResponse(status_code=exc.status_code, content={"code":exc.status_code,"msg":str(exc.detail)})
"""
程序基本配置
作用：读取.env文件的配置项
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 告诉pydantic_settings: 去哪里读取配置文件
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    # 文件上传路径
    fast_profile: str = "./file"

    # 数据库配置
    db_host: str = ""
    db_port: int = 3306
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""

    # 后端端口
    server_port: int = 8080

    # token配置
    # 请求头的字段名: 前端需要在请求头携带此字段传递token
    token_header: str = "Authorization"
    # 令牌密钥: 前后端约定好的"暗号", 用于加密/解密token
    token_secret: str = ""
    # 令牌有效期(分钟), 过期后需要重新登录
    token_expire_time: int = 3000

    @property
    def database_url(self) -> str:
        """
        数据库连接地址(pymysql格式)
        拼接后的完整地址类似:
        mysql+pymysql://root:密码@localhost:3306/fastapi?charset=utf8mb4
        """
        return (
            f"mysql+asyncmy://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )
# 创建全局配置对象: 其他文件直接 from app.core.config import settings 使用即可
settings = Settings()
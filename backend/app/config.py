"""
应用配置：从环境变量读取，支持 .env
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用
    app_name: str = "QA Admin Backend"
    debug: bool = False
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    # MySQL: 本机 root/root 端口 13307
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 13307
    mysql_user: str = "root"
    mysql_password: str = "root"
    mysql_database: str = "qa_admin"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    @property
    def database_url_sync(self) -> str:
        """同步 URL，供 Alembic 迁移使用"""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    # JWT
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 天

    # Redis（可选，未配置则不用缓存）
    redis_url: str = "redis://127.0.0.1:6379/0"

    # CORS
    cors_origins: list[str] = ["*"]


settings = Settings()

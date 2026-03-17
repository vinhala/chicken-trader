from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "AI Investment Opportunity MVP"
    secret_key: str = "change_me"
    access_token_expire_minutes: int = 1440
    postgres_user: str = "app"
    postgres_password: str = "app"
    postgres_db: str = "investment_app"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    news_api_key: str = ""
    news_api_base_url: str = "https://newsapi.org/v2"
    market_api_key: str = ""
    market_api_base_url: str = "https://finnhub.io/api/v1"
    eodhd_api_key: str = ""
    eodhd_api_base_url: str = "https://eodhd.com/api"
    openai_api_key: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "no-reply@example.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @model_validator(mode="after")
    def populate_connection_urls(self) -> "Settings":
        if not self.database_url:
            self.database_url = (
                f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        if not self.redis_url:
            self.redis_url = f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return self


settings = Settings()

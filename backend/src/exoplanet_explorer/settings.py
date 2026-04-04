"""Application settings loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(..., alias="NAME")
    debug: bool = Field(..., alias="DEBUG")
    address: str = Field(..., alias="ADDRESS")
    port: int = Field(..., alias="PORT")
    reload: bool = Field(..., alias="RELOAD")

    api_key: str = Field(..., alias="API_KEY")

    cors_origins: list[str] = Field(..., alias="CORS_ORIGINS")

    db_host: str = Field(..., alias="DB_HOST")
    db_port: int = Field(..., alias="DB_PORT")
    db_name: str = Field(..., alias="DB_NAME")
    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")


settings = Settings.model_validate({})

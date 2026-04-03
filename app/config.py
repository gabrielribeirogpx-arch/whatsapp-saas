from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WhatsApp SaaS API"
    api_prefix: str = "/api"
    database_url: str = Field(default="postgresql+psycopg://postgres:postgres@localhost:5432/whatsapp_saas")
    meta_graph_version: str = "v20.0"
    verify_token: str = Field(default="dev-verify-token")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

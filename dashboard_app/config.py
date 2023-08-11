from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


class ClientSettings(AppSettings):
    name: str
    base_url: str


class Settings(AppSettings):
    """Settings for the application"""

    xclient: ClientSettings
    port: int = 5000
    host: str = "127.0.0.1"

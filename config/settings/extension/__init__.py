from pydantic import BaseSettings


class BaseSettingWithProperties(BaseSettings):
    @classmethod
    def get_properties(cls):
        return [prop for prop in dir(cls) if isinstance(getattr(cls, prop), property)]

    def dict(self, *args, **kwargs):
        """Override dict() to include properties"""
        self.__dict__.update(
            {prop: getattr(self, prop) for prop in self.get_properties()}
        )
        return super().dict(*args, **kwargs)

    def json(
        self,
        *args,
        **kwargs,
    ) -> str:
        """Override json() to include properties"""
        self.__dict__.update(
            {prop: getattr(self, prop) for prop in self.get_properties()}
        )

        return super().json(*args, **kwargs)


class DbEngine(BaseSettings):
    """Manage Engine settings only"""

    ENGINE: str = "django.db.backends.sqlite3"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class SQLiteSettings(DbEngine):
    """Manage sqlite settings only"""

    NAME: str = "db.sqlite3"


class PostgresSettings(BaseSettings):
    ENGINE: str = "django.db.backends.postgresql"
    NAME: str
    HOST: str
    PORT: str
    USER: str
    PASSWORD: str

    class Config:
        env_prefix = "POSTGRES_"
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


class DatabaseSettings(BaseSettings):
    """Manage databases settings"""

    default: SQLiteSettings | PostgresSettings

    @classmethod
    def get_db_settings(cls):
        engine: DbEngine = DbEngine()
        if "postgres" in engine.ENGINE:
            return cls(default=PostgresSettings())  # type: ignore
        return cls(default=SQLiteSettings())


class BaseEnv(BaseSettings):
    DEBUG: bool = True
    SECRET_KEY: str = (
        "django-insecure-!*f!8&^-h8oi0+)=r5rv0mifpem=@l18wr&3d!d06@be)@u53w"
    )
    ALLOWED_HOSTS: list[str] = ["*"]
    DATABASES: DatabaseSettings = DatabaseSettings.get_db_settings()
    STATIC_URL: str = "assets/"
    AUTH_USER_MODEL: str = "authentication.User"
    INTERNAL_IPS: tuple = ("127.0.0.1",)
    ROOT_URLCONF: str = "config.urls"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class EnvironSettings(BaseEnv):
    pass


class RemoteSettings(BaseEnv, BaseSettingWithProperties):
    DEBUG: bool = False
    PROD_URI: str = "dashboard.service"
    CSRF_COOKIE_SECURE: bool = True
    STATICFILES_STORAGE: str = "whitenoise.storage.CompressedManifestStaticFilesStorage"

    @property
    def prod_uri_https(self) -> str:
        return f"https://{self.PROD_URI}"

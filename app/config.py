import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_name: str
    database_username: str
    database_password: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # direct Neon connection, mainly for Alembic / migrations
    direct_database_url: str | None = None

    # for app/runtime connections
    database_sslmode: str = (
        "disable"  # default to disable for local development, but in production this should be set to "require" or "verify-full"
    )

    model_config = SettingsConfigDict(
        env_file=".env.local",
        extra="ignore",
    )

    @property
    def app_database_url(self) -> str:
        return (
            f"postgresql://{self.database_username}:"
            f"{self.database_password}@{self.database_hostname}:"
            f"{self.database_port}/{self.database_name}"
        )

    @property
    def migration_database_url(self) -> str:
        return self.direct_database_url or self.app_database_url


# Optional override for unusual cases like tests/CI
_env_file = os.getenv("ENV_FILE")
settings = Settings(_env_file=_env_file) if _env_file else Settings()

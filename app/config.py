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

    direct_database_url: str | None = None  # Optional override for direct database URL
    database_sslmode: str = (
        "disable"  # Optional SSL mode for database connection, default is "disable"
    )
    testing: bool = (
        False  # Flag to indicate if the application is running in testing mode, default is False
    )

    model_config = SettingsConfigDict(
        env_file=".env.local",
        extra="ignore",
    )

    @property
    def resolved_database_name(self) -> str:
        return f"{self.database_name}_test" if self.testing else self.database_name

    @property
    def app_database_url(self) -> str:
        return (
            f"postgresql://{self.database_username}:"
            f"{self.database_password}@{self.database_hostname}:"
            f"{self.database_port}/{self.resolved_database_name}"
        )

    @property
    def migration_database_url(self) -> str:
        return self.direct_database_url or self.app_database_url


# Optional override for unusual cases like tests/CI
_env_file = os.getenv("ENV_FILE")
settings = Settings(_env_file=_env_file) if _env_file else Settings()

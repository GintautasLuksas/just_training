from dataclasses import dataclass
import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL


load_dotenv()


@dataclass(frozen=True)
class Settings:
    db_host: str
    db_port: str
    db_name: str
    db_user: str
    db_password: str
    app_schema: str = "sql_trainer"
    practice_schema: str = "practice"

    @property
    def sqlalchemy_url(self) -> URL:
        return URL.create(
            "postgresql+pg8000",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=int(self.db_port),
            database=self.db_name,
        )


def get_settings() -> Settings:
    load_dotenv(override=True)
    settings = Settings(
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=os.getenv("DB_PORT", "5432"),
        db_name=os.getenv("DB_NAME", ""),
        db_user=os.getenv("DB_USER", ""),
        db_password=os.getenv("DB_PASSWORD", ""),
    )
    missing = [
        name
        for name, value in {
            "DB_NAME": settings.db_name,
            "DB_USER": settings.db_user,
            "DB_PASSWORD": settings.db_password,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing database environment variables: {', '.join(missing)}")
    return settings

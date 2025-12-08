import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    url: str = os.getenv("DATABASE_URL", "")
    
    @property
    def async_url(self) -> str:
        if self.url.startswith("postgres://"):
            return self.url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif self.url.startswith("postgresql://"):
            return self.url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.url


@dataclass
class RedisConfig:
    url: str = os.getenv("REDIS_URL", "redis://localhost:6379")


@dataclass
class BotConfig:
    token: str = os.getenv("BOT_TOKEN", "")
    admin_username: str = os.getenv("ADMIN_USERNAME", "@Admin")
    root_admin_id: int = int(os.getenv("ROOT_ADMIN_ID", "0"))


@dataclass
class Config:
    db: DatabaseConfig = None
    redis: RedisConfig = None
    bot: BotConfig = None
    
    def __post_init__(self):
        self.db = DatabaseConfig()
        self.redis = RedisConfig()
        self.bot = BotConfig()


config = Config()

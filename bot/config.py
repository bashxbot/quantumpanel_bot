import os
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs, urlencode
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    url: str = os.getenv("DATABASE_URL", "")
    
    @property
    def async_url(self) -> str:
        url = self.url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        if "sslmode=" in url:
            url = url.replace("sslmode=disable", "").replace("sslmode=require", "")
            url = url.replace("?&", "?").replace("&&", "&")
            if url.endswith("?") or url.endswith("&"):
                url = url[:-1]
        
        return url


@dataclass
class RedisConfig:
    url: str = os.getenv("REDIS_URL", "redis://default:ARTvAAImcDE0YWZlMWU2MjAwNDY0NmFiYTU4OTdkNjEwZDA5ZDE1ZnAxNTM1OQ@obliging-hare-5359.upstash.io:6379")


@dataclass
class BotConfig:
    token: str = os.getenv("BOT_TOKEN", "")
    admin_username: str = os.getenv("ADMIN_USERNAME", "@Admin")
    root_admin_id: int = int(os.getenv("ROOT_ADMIN_ID") or "0")
    report_channel: str = os.getenv("REPORT_CHANNEL", "")
    maintenance_mode: bool = False


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

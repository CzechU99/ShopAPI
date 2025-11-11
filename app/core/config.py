from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://shop:shop@db:5432/shopdb"
    EXTERNAL_SERVICE_URL: str = "http://external_service:8001"

    # External HTTP client tuning knobs
    EXT_CLIENT_CONNECT_TIMEOUT: float = 2.0
    EXT_CLIENT_READ_TIMEOUT: float = 180.0
    EXT_CLIENT_WRITE_TIMEOUT: float = 5.0
    EXT_CLIENT_POOL_TIMEOUT: float = 0.05
    EXT_CLIENT_MAX_CONNECTIONS: int = 100
    EXT_CLIENT_MAX_KEEPALIVE_CONNECTIONS: int = 20
    EXT_CLIENT_KEEPALIVE_EXPIRY: float = 5.0
    EXT_CLIENT_HTTP2_ENABLED: bool = True

    model_config = ConfigDict(env_file=".env")

settings = Settings()

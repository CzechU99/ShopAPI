from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://shop:shop@db:5432/shopdb"
    EXTERNAL_SERVICE_URL: str = "http://external_service:8001"
    EXTERNAL_SERVICE_HTTP2_URL: str = "https://external_service:8443"

    EXT_CLIENT_CONNECT_TIMEOUT: float = 2.0
    EXT_CLIENT_READ_TIMEOUT: float = 180.0
    EXT_CLIENT_WRITE_TIMEOUT: float = 5.0
    EXT_CLIENT_POOL_TIMEOUT: float = 1.0
    EXT_CLIENT_MAX_CONNECTIONS: int = 200
    EXT_CLIENT_MAX_KEEPALIVE_CONNECTIONS: int = 50
    EXT_CLIENT_KEEPALIVE_EXPIRY: float = 5.0
    EXT_CLIENT_HTTP2_ENABLED: bool = False
    EXT_CLIENT_CA_CERT: str | None = "/app/certs/local_ca.crt"

    MESSAGE_BROKER_DEFAULT: str = "kafka"
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_ASYNC_UPSTREAM_TOPIC: str = "external_async_upstream"
    KAFKA_ASYNC_DOWNSTREAM_TOPIC: str = "external_async_downstream"

    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    RABBITMQ_ASYNC_UPSTREAM_QUEUE: str = "external_async_upstream"
    RABBITMQ_ASYNC_DOWNSTREAM_QUEUE: str = "external_async_downstream"

    model_config = ConfigDict(env_file=".env")


settings = Settings()

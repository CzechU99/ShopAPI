from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://shop:shop@db:5432/shopdb"

    class Config:
        env_file = ".env"

settings = Settings()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # PostgreSQL
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "url_shortener"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    class Config:
        env_file = ".env"

settings = Settings()

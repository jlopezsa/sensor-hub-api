from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Sensor Hub API"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    DATABASE_URL: str = "postgresql+psycopg://user:password@localhost:5432/sensor_hub"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignora variables no usadas (compatibilidad con API_V1_STR)
    )


settings = Settings()

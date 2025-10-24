from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Sensor Hub API"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignora variables no usadas (compatibilidad con API_V1_STR)
    )


settings = Settings()

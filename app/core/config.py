from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Sensor Hub API"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    DATABASE_URL: str = "postgresql+psycopg://user:password@localhost:5432/sensor_hub"
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    MQTT_CLIENT_ID: Optional[str] = None
    MQTT_SUBSCRIBE_TOPICS: Optional[str] = "sensors/#"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignora variables no usadas (compatibilidad con API_V1_STR)
    )


settings = Settings()

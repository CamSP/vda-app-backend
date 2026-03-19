from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Encuentro APP"
    GOOGLE_MAPS_API_KEY: str
    API_KEY: str
    DATABASE_URL: str
    EXPO_ACCESS_TOKEN: str
    GOOGLE_SERVICE_ACCOUNT_JSON: str
    WORDPRESS_URL: str
    WORDPRESS_API_KEY: str
    GOOGLE_CALENDAR_ID: str

    class Config:
        env_file = "./.env"

settings = Settings()
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Encuentro APP"
    GOOGLE_MAPS_API_KEY: str
    API_KEY: str
    DATABASE_URL: str
    EXPO_ACCESS_TOKEN: str

    class Config:
        env_file = "./.env"

settings = Settings()
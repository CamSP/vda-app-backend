from e import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Encuentro APP"
    GOOGLE_MAPS_API_KEY: str
    API_KEY: str
    DATABASE_URL: str

    class Config:
        env_file = "../.env"

settings = Settings()
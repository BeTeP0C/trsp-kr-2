from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "change-me"
    session_duration: int = 300
    renewal_threshold: int = 180

    mode: str = "DEV"
    docs_user: str = "admin"
    docs_password: str = "admin"
    jwt_expiration_minutes: int = 30

    model_config = {"env_file": ".env"}


settings = Settings()

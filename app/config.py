from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "change-me"
    session_duration: int = 300
    renewal_threshold: int = 180

    model_config = {"env_file": ".env"}


settings = Settings()

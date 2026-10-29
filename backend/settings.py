from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    encryption_key: str
    # Public HTTPS base url Pluggy reaches this backend at (e.g. an ngrok url). Unset skips the webhook registration
    public_base_url: str | None = None


settings = Settings()  # type: ignore

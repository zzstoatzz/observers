from pathlib import Path
from typing import Self
from zoneinfo import ZoneInfo

from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    log_level: str = 'INFO'
    timezone: str = 'America/Chicago'

    app_dir: Path = Path('~/.config/observers').expanduser()

    @computed_field
    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)

    @model_validator(mode='after')
    def ensure_logging_setup(self) -> Self:
        from observers.loggers import setup_logging

        setup_logging(self.log_level)
        self.app_dir.mkdir(parents=True, exist_ok=True)
        return self


settings = Settings()

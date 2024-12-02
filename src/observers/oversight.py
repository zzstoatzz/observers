import os

from humanlayer import ContactChannel, HumanLayer, SlackContactChannel
from pydantic import (
    Field,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_default_contact_channel() -> ContactChannel:
    if not (testing_user := os.getenv('TESTING_USER')):
        return ContactChannel()

    return ContactChannel(
        slack=SlackContactChannel(
            channel_or_user_id='',
            context_about_channel_or_user=f'a dm with {testing_user.lower()}',
            experimental_slack_blocks=True,
        )
    )


class HumanLayerSettings(BaseSettings):
    """Settings for the HumanLayer"""

    model_config = SettingsConfigDict(
        env_file='.env', extra='ignore', env_prefix='HUMANLAYER_'
    )

    api_key: str | None = Field(default=None, description='HumanLayer API key')
    slack: ContactChannel | None = Field(
        default_factory=get_default_contact_channel
    )

    @computed_field
    @property
    def instance(self) -> HumanLayer:
        """HumanLayer instance"""
        return HumanLayer(api_key=self.api_key, contact_channel=self.slack)

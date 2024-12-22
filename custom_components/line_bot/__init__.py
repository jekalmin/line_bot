"""The line_bot component."""

import logging

from linebot.models import (
    AudioSendMessage,
    ButtonsTemplate,
    ConfirmTemplate,
    FlexSendMessage,
    ImageSendMessage,
    LocationSendMessage,
    MessageAction,
    PostbackAction,
    StickerSendMessage,
    TemplateSendMessage,
    TextSendMessage,
    URIAction,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .helpers import get_quota
from .http import async_register_http
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

MESSAGES = {
    "text": TextSendMessage,
    "image": ImageSendMessage,
    "sticker": StickerSendMessage,
    "template": TemplateSendMessage,
    "location": LocationSendMessage,
    "flex": FlexSendMessage,
    "audio": AudioSendMessage,
}


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up OpenAI Conversation."""
    await async_setup_services(hass, config)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenAI Conversation from a config entry."""

    await get_quota(hass, entry.data[CONF_ACCESS_TOKEN])
    hass.data.setdefault(DOMAIN, {}).setdefault("entry", {}).setdefault(
        entry.entry_id, {}
    )

    async_register_http(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload OpenAI."""
    hass.data[DOMAIN]["entry"].pop(entry.entry_id)
    return True

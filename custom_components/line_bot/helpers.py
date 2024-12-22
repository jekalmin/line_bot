"""Helper functions for Line Bot integration."""

from functools import partial

from linebot import LineBotApi

from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def get_quota(hass: HomeAssistant, access_token: str):
    """Get quota for the Line Bot API."""
    line_bot = LineBotApi(access_token)

    await hass.loop.run_in_executor(
        None, partial(line_bot.get_message_quota_consumption)
    )


def get_config_entry(hass: HomeAssistant):
    """Get the config entry."""
    entry_data = hass.data.get(DOMAIN, {}).get("entry", {})
    entry_id, data = next(iter(entry_data.items()), (None, None))
    return hass.config_entries.async_get_entry(entry_id)


def get_data(hass: HomeAssistant):
    """Get the data."""
    entry_id, data = next(iter(hass.data[DOMAIN]["entry"].items()))
    return data

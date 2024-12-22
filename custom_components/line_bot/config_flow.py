"""Config flow for Line Bot integration."""

from __future__ import annotations

import logging
from typing import Any

from linebot.exceptions import LineBotApiError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_ACTION, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
)

from .const import (
    CONF_ACTION_ADD_CHAT,
    CONF_ACTION_REMOVE_CHAT,
    CONF_ALLOWED_CHAT_IDS,
    CONF_CHANNEL_SECRET,
    CONF_CHAT_ID,
    CONF_NEW_MESSAGES,
    DOMAIN,
)
from .helpers import get_quota

_LOGGER = logging.getLogger(__name__)

CONF_ACTIONS = {
    CONF_ACTION_ADD_CHAT: "Add a chat",
    CONF_ACTION_REMOVE_CHAT: "Remove a chat",
}

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
        vol.Required(CONF_CHANNEL_SECRET): cv.string,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    access_token = data[CONF_ACCESS_TOKEN]
    await get_quota(hass, access_token)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenAI Conversation."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}
        try:
            await validate_input(self.hass, user_input)
        except LineBotApiError:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title="Line Bot", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return LineBotOptionsFlow(config_entry)


class LineBotOptionsFlow(config_entries.OptionsFlow):
    """OpenAI config flow options handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.selected_chat = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            if user_input.get(CONF_ACTION) == "add_chat":
                return await self.async_step_add_chat()
            if user_input.get(CONF_ACTION) == "remove_chat":
                return await self.async_step_remove_chat()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({vol.Required(CONF_ACTION): vol.In(CONF_ACTIONS)}),
        )

    async def async_step_add_chat(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a chat."""
        self.selected_chat = None
        errors = {}
        if user_input is not None:
            if user_input.get(CONF_NEW_MESSAGES) is not None:
                self.selected_chat = user_input[CONF_NEW_MESSAGES]
                return await self.async_step_configure_chat(user_input)

        new_messages = self.get_new_messages()
        return self.async_show_form(
            step_id="add_chat",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NEW_MESSAGES): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(
                                    value=key,
                                    label=f"{key[:5]} ({value.message.text})",
                                )
                                for key, value in new_messages.items()
                            ],
                        )
                    ),
                }
            ),
        )

    async def async_step_configure_chat(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure a chat."""
        chat_id = self.selected_chat
        if user_input.get(CONF_NAME) is not None:
            new_data = self.config_entry.data.copy()
            allowed_chat_ids = new_data.get(CONF_ALLOWED_CHAT_IDS, {}).copy()
            allowed_chat_ids.update(
                {user_input.get(CONF_NAME): {CONF_CHAT_ID: chat_id}}
            )
            new_data[CONF_ALLOWED_CHAT_IDS] = allowed_chat_ids

            self.get_new_messages().pop(chat_id)
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=new_data,
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="configure_chat",
            data_schema=vol.Schema({vol.Required(CONF_NAME): str}),
        )

    async def async_step_remove_chat(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Remove a chat."""
        if user_input is not None:
            new_data = self.config_entry.data.copy()
            allowed_chat_ids = new_data.get(CONF_ALLOWED_CHAT_IDS, {})
            new_allowed_chat_ids = {
                key: value
                for key, value in allowed_chat_ids.items()
                if key not in user_input.get(CONF_ALLOWED_CHAT_IDS, [])
            }
            new_data[CONF_ALLOWED_CHAT_IDS] = new_allowed_chat_ids

            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=new_data,
            )
            return self.async_create_entry(title="", data={})

        allowed_chat_ids = list(
            self.config_entry.data.get(CONF_ALLOWED_CHAT_IDS, {}).keys()
        )

        return self.async_show_form(
            step_id="remove_chat",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_ALLOWED_CHAT_IDS): SelectSelector(
                        SelectSelectorConfig(
                            options=allowed_chat_ids,
                            multiple=True,
                        )
                    ),
                }
            ),
        )

    def get_new_messages(self):
        """Get new messages."""
        return next(iter(self.hass.data[DOMAIN]["entry"].values())).get(
            CONF_NEW_MESSAGES, {}
        )

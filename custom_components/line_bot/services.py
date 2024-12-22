"""Services for the Line Bot integration."""

from functools import partial
import logging

from linebot import LineBotApi
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
import voluptuous as vol

from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse
from homeassistant.helpers import config_validation as cv, selector
from homeassistant.helpers.typing import ConfigType

from .const import CONF_ALLOWED_CHAT_IDS, CONF_CHAT_ID, DOMAIN
from .exceptions import ChatIdNotFound
from .helpers import get_config_entry

QUERY_IMAGE_SCHEMA = vol.Schema(
    {
        vol.Required("config_entry"): selector.ConfigEntrySelector(
            {
                "integration": DOMAIN,
            }
        ),
        vol.Required("model", default="gpt-4-vision-preview"): cv.string,
        vol.Required("prompt"): cv.string,
        vol.Required("images"): vol.All(cv.ensure_list, [{"url": cv.string}]),
        vol.Optional("max_tokens", default=300): cv.positive_int,
    }
)

MESSAGES = {
    "text": TextSendMessage,
    "image": ImageSendMessage,
    "sticker": StickerSendMessage,
    "template": TemplateSendMessage,
    "location": LocationSendMessage,
    "flex": FlexSendMessage,
    "audio": AudioSendMessage,
}

_LOGGER = logging.getLogger(__package__)


async def async_setup_services(hass: HomeAssistant, config: ConfigType) -> None:
    """Set up services for the Line Bot integration."""

    line_notification_service = LineNotificationService(hass)

    async def send_message(call: ServiceCall) -> ServiceResponse:
        """Send a message."""
        to = call.data.get("to")
        reply_token = call.data.get("reply_token")
        message = call.data.get("message")
        message_type = message.get("type")
        return await line_notification_service.send_message(
            MESSAGES[message_type].new_from_json_dict(message),
            to=to,
            reply_token=reply_token,
        )

    async def send_button_message(call: ServiceCall) -> ServiceResponse:
        """Send a button message."""
        to = call.data.get("to")
        reply_token = call.data.get("reply_token")
        text = call.data.get("text")
        alt_text = call.data.get("alt_text", text)
        buttons = call.data.get("buttons")
        button_template = ButtonsTemplate(text=text, actions=to_actions(buttons))
        return await line_notification_service.send_message(
            TemplateSendMessage(alt_text=alt_text, template=button_template),
            to=to,
            reply_token=reply_token,
        )

    async def send_confirm_message(call: ServiceCall) -> ServiceResponse:
        """Send a confirm message."""
        to = call.data.get("to")
        reply_token = call.data.get("reply_token")
        text = call.data.get("text")
        alt_text = call.data.get("altText", text)
        buttons = call.data.get("buttons")
        confirm_template = ConfirmTemplate(text=text, actions=to_actions(buttons))
        return await line_notification_service.send_message(
            TemplateSendMessage(alt_text=alt_text, template=confirm_template),
            to=to,
            reply_token=reply_token,
        )

    hass.services.async_register(DOMAIN, "send_message", send_message)
    hass.services.async_register(DOMAIN, "send_button_message", send_button_message)
    hass.services.async_register(DOMAIN, "send_confirm_message", send_confirm_message)
    return True


class LineNotificationService:
    """Service for sending Line notifications."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the service."""
        self.hass = hass

    def get_line_bot_api(self):
        """Get the Line Bot API."""
        data = get_config_entry(self.hass).data
        return LineBotApi(data[CONF_ACCESS_TOKEN])

    def get_allowed_chat_ids(self):
        """Get the allowed chat IDs."""
        config_entry_data = get_config_entry(self.hass).data
        return config_entry_data.get(CONF_ALLOWED_CHAT_IDS, {})

    async def send_message(self, message, **kwargs):
        """Send a message."""
        reply_token = kwargs.get("reply_token")
        if reply_token:
            return await self.hass.loop.run_in_executor(
                None,
                partial(self.get_line_bot_api().reply_message, reply_token, message),
            )

        to = self.get_allowed_chat_ids().get(kwargs.get("to"), {}).get(CONF_CHAT_ID)
        if to is None:
            raise ChatIdNotFound(kwargs.get("to"), self.get_allowed_chat_ids())
        return await self.hass.loop.run_in_executor(
            None,
            partial(self.get_line_bot_api().push_message, to, message),
        )


def to_actions(buttons):
    """Convert a list of buttons to a list of actions."""
    actions = []
    for button in buttons:
        action = None
        text = button.get("text")
        data = button.get("data")
        uri = button.get("uri")
        if data is not None:
            label = button.get("label", text)
            action = PostbackAction(label=label, data=data)
        elif uri is not None:
            label = button.get("label", text)
            action = URIAction(label=label, uri=uri)
        else:
            label = button.get("label", text)
            action = MessageAction(label=label, text=text)
        actions.append(action)
    return actions

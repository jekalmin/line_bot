import logging
import requests
import voluptuous as vol
from typing import Any, Dict
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import CONF_TOKEN
from urllib.parse import urlencode

from .http import async_register_http
from .const import (
    DOMAIN, CONF_ALLOWED_CHAT_IDS, CONF_SECRET
)
from linebot import (
    LineBotApi
)
from linebot.models import (
    TextSendMessage,
    ImageSendMessage,
    StickerSendMessage,
    TemplateSendMessage,
    LocationSendMessage,
    FlexSendMessage,
    AudioSendMessage,
    ButtonsTemplate,
    ConfirmTemplate,
    PostbackAction,
    URIAction,
    MessageAction,
)

_LOGGER = logging.getLogger(__name__)

MESSAGES = {
    "text": TextSendMessage,
    "image": ImageSendMessage,
    "sticker": StickerSendMessage,
    "template": TemplateSendMessage,
    "location": LocationSendMessage,
    "flex": FlexSendMessage,
    "audio": AudioSendMessage
}

def setup(hass: HomeAssistant, config: Dict[str, Any]):
    if config[DOMAIN].get(CONF_SECRET):
        async_register_http(hass, config)

    lineClient = LineNotificationService(config[DOMAIN].get(CONF_TOKEN), config[DOMAIN].get(CONF_ALLOWED_CHAT_IDS, {}))

    def send_message(call):
        to = call.data.get("to")
        reply_token = call.data.get("reply_token")
        message = call.data.get("message")
        message_type = message.get("type")
        lineClient.send_message(MESSAGES[message_type].new_from_json_dict(message), to=to, reply_token=reply_token)

    def send_button_message(call):
        to = call.data.get("to")
        reply_token = call.data.get("reply_token")
        message = call.data.get("message")
        alt_text = call.data.get("alt_text", message)
        buttons = call.data.get("buttons")
        button_template = ButtonsTemplate(text=message, actions=to_actions(buttons))
        lineClient.send_message(TemplateSendMessage(alt_text=alt_text, template=button_template), to=to, reply_token=reply_token)

    def send_confirm_message(call):
        to = call.data.get("to")
        reply_token = call.data.get("reply_token")
        message = call.data.get("message")
        alt_text = call.data.get("altText", message)
        buttons = call.data.get("buttons")
        confirm_template = ConfirmTemplate(text=message, actions=to_actions(buttons))
        lineClient.send_message(TemplateSendMessage(alt_text=alt_text, template=confirm_template), to=to, reply_token=reply_token)

    hass.services.register(DOMAIN, 'send_message', send_message)
    hass.services.register(DOMAIN, 'send_button_message', send_button_message)
    hass.services.register(DOMAIN, 'send_confirm_message', send_confirm_message)
    return True

class LineNotificationService:
    def __init__(self, token, allowed_chat_ids):
        """Initialize the service."""
        self.allowed_chat_ids = allowed_chat_ids
        self.line_bot_api = LineBotApi(token)

    def send_message(self, message, **kwargs):
        reply_token = kwargs.get("reply_token")
        if reply_token:
            self.line_bot_api.reply_message(reply_token, message)
        else:
            to = self.allowed_chat_ids.get(kwargs.get("to"))
            self.line_bot_api.push_message(to, message)

def to_actions(buttons):
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
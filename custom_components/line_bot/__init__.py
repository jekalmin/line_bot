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

    allowed_chat_ids = config[DOMAIN].get(CONF_ALLOWED_CHAT_IDS, {})
    line_bot_api = LineBotApi(config[DOMAIN].get(CONF_TOKEN))

    def reply_message(call):
        reply_token = call.data.get("reply_token")
        message = call.data.get("message")
        message_type = message.get("type")
        line_bot_api.reply_message(reply_token, MESSAGES[message_type].new_from_json_dict(message))

    def push_message(call):
        to = call.data.get("to")
        message = call.data.get("message")
        message_type = message.get("type")
        line_bot_api.push_message(allowed_chat_ids.get(to), MESSAGES[message_type].new_from_json_dict(message))

    hass.services.register(DOMAIN, 'reply_message', reply_message)
    hass.services.register(DOMAIN, 'push_message', push_message)
    return True
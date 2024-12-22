"""Webhook for Line Bot."""

import logging
from urllib.parse import parse_qsl

from aiohttp.web import Request, Response
from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    PostbackEvent,
    SourceGroup,
    SourceRoom,
    TextSendMessage,
)

from homeassistant.components.http import HomeAssistantView
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant, callback
from homeassistant.util.decorator import Registry

from .const import (
    CONF_ALLOWED_CHAT_IDS,
    CONF_CHANNEL_SECRET,
    CONF_CHAT_ID,
    CONF_NEW_MESSAGES,
    EVENT_WEBHOOK_POSTBACK_RECEIVED,
    EVENT_WEBHOOK_TEXT_RECEIVED,
)
from .helpers import get_config_entry, get_data

HANDLERS = Registry()
_LOGGER = logging.getLogger(__name__)


@callback
def async_register_http(hass: HomeAssistant):
    """Register the webhook."""
    hass.http.register_view(LineWebhookView(hass))


class LineWebhookView(HomeAssistantView):
    """Handle Line Webhook."""

    url = "/api/line/callback"
    name = "api:line_bot"
    requires_auth = False

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the view."""
        self.hass = hass
        config_entry_data = get_config_entry(hass).data
        self.line_bot_api = LineBotApi(config_entry_data[CONF_ACCESS_TOKEN])
        self.parser = WebhookParser(config_entry_data.get(CONF_CHANNEL_SECRET))

    async def post(self, request: Request) -> Response:
        """Handle Webhook."""
        config_entry = get_config_entry(self.hass)
        if config_entry is None:
            raise HTTPNotFound

        # get X-Line-Signature header value
        signature = request.headers["X-Line-Signature"]
        body = await request.text()
        # parse webhook body
        try:
            events = self.parser.parse(body, signature)
        except InvalidSignatureError as e:
            _LOGGER.error(e)
            raise HTTPBadRequest from e

        for event in events:
            if self.is_test(event.reply_token):
                return "OK"
            if not self.is_allowed(event):
                chat_id = self.get_chat_id(event.source)
                get_data(self.hass).setdefault(CONF_NEW_MESSAGES, {})[chat_id] = event
                raise HTTPBadRequest

            handler_keys = [event.__class__.__name__]
            if hasattr(event, "message"):
                handler_keys.append(event.message.__class__.__name__)
            handler = HANDLERS.get("_".join(handler_keys))
            handler(self.hass, self.line_bot_api, event)
        return "OK"

    def is_test(self, reply_token):
        """Check if the event is a test event."""
        if reply_token == "00000000000000000000000000000000":
            return True
        return False

    def get_chat_id(self, source):
        """Get chat id from source."""
        if source.type == "user":
            return source.user_id
        elif source.type == "group":
            return source.group_id
        elif source.type == "room":
            return source.room_id
        return None

    def is_allowed(self, event):
        """Check if the event is allowed."""
        return self.get_chat_id(event.source) in self.get_allowed_chat_ids()

    def get_allowed_chat_ids(self):
        """Get allowed chat ids."""
        config_entry_data = get_config_entry(self.hass).data
        return [
            value[CONF_CHAT_ID]
            for value in config_entry_data.get(CONF_ALLOWED_CHAT_IDS, {}).values()
        ]


@HANDLERS.register("MessageEvent_TextMessage")
def handle_message_event_text_message(
    hass: HomeAssistant, line_bot_api: LineBotApi, event: MessageEvent
):
    """Handle text message."""
    text = event.message.text
    if text == "bye":
        exit_chat(line_bot_api, event)
        return

    hass.bus.fire(
        EVENT_WEBHOOK_TEXT_RECEIVED,
        {
            "reply_token": event.reply_token,
            "event": event.as_json_dict(),
            "content": event.message.as_json_dict(),
            "text": event.message.text,
        },
    )


@HANDLERS.register("PostbackEvent")
def handle_postback_event_message(
    hass: HomeAssistant, line_bot_api: LineBotApi, event: PostbackEvent
):
    """Handle postback."""
    hass.bus.fire(
        EVENT_WEBHOOK_POSTBACK_RECEIVED,
        {
            "reply_token": event.reply_token,
            "event": event.as_json_dict(),
            "content": event.postback.as_json_dict(),
            "data": event.postback.data,
            "data_json": dict(parse_qsl(event.postback.data)),
            "params": event.postback.params,
        },
    )


def exit_chat(line_bot_api: LineBotApi, event: MessageEvent):
    """Exit chat."""
    if isinstance(event.source, SourceGroup):
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="Leaving group")
        )
        line_bot_api.leave_group(event.source.group_id)
    elif isinstance(event.source, SourceRoom):
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="Leaving group")
        )
        line_bot_api.leave_room(event.source.room_id)
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="Bot can't leave from 1:1 chat")
        )

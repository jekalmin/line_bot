import logging
import json
from typing import Any, Dict
from homeassistant.const import CONF_TOKEN
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant, callback
from homeassistant.util.decorator import Registry
from urllib.parse import parse_qsl
from aiohttp.web import Request, Response
from aiohttp.web_exceptions import HTTPBadRequest
from .const import (
    DOMAIN, CONF_SECRET, CONF_ALLOWED_CHAT_IDS, EVENT_WEBHOOK_TEXT_RECEIVED, EVENT_WEBHOOK_POSTBACK_RECEIVED
)
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage
)

HANDLERS = Registry()
_LOGGER = logging.getLogger(__name__)

@callback
def async_register_http(hass: HomeAssistant, config: Dict[str, Any]):
    lineBotConfig = LineBotConfig(hass, config)
    hass.http.register_view(LineWebhookView(lineBotConfig))

class LineBotConfig:
    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]):
        """Initialize the config."""
        self.hass = hass
        self.config = config
        self.channel_access_token = config[DOMAIN].get(CONF_TOKEN)
        self.channel_secret = config[DOMAIN].get(CONF_SECRET)
        self.allowed_chat_ids = config[DOMAIN].get(CONF_ALLOWED_CHAT_IDS, {})

class LineWebhookView(HomeAssistantView):
    url = "/api/line/callback"
    name = "api:line_bot"
    requires_auth = False

    def __init__(self, config: LineBotConfig):
        self.config = config
        self.line_bot_api = LineBotApi(config.channel_access_token)
        self.parser = WebhookParser(config.channel_secret)

    async def post(self, request: Request) -> Response:
        """Handle Webhook"""
        # get X-Line-Signature header value
        signature = request.headers['X-Line-Signature']
        body = await request.text()

        # parse webhook body
        try:
            events = self.parser.parse(body, signature)
        except InvalidSignatureError:
            raise HTTPBadRequest()

        for event in events:
            if self.is_test(event.reply_token):
                return 'OK'
            if not self.is_allowed(event):
                self.notify(event)
                raise HTTPBadRequest()

            handler_keys = [event.__class__.__name__]
            if hasattr(event, 'message'):
                handler_keys.append(event.message.__class__.__name__)
            handler = HANDLERS.get("_".join(handler_keys))
            handler(self.config.hass, self.line_bot_api, event)
        return 'OK'

    def is_test(self, reply_token):
        if reply_token == '00000000000000000000000000000000':
            return True
        return False

    def get_chat_id(self, source):
        if source.type == 'user':
            return source.user_id
        elif source.type == 'group':
            return source.group_id
        elif source.type == 'room':
            return source.room_id
        return None

    def is_allowed(self, event):
        return self.get_chat_id(event.source) in self.config.allowed_chat_ids.values()

    def notify(self, event):
        chat_id = self.get_chat_id(event.source)
        event_json = json.dumps(event, default=lambda x: x.__dict__, ensure_ascii=False)
        message = f"chat_id: {chat_id}\n\nevent: {event_json}"
        self.config.hass.components.persistent_notification.create(message, title="LineBot Request From Unknown ChatId", notification_id=chat_id)

@HANDLERS.register("MessageEvent_TextMessage")
def handle_message(hass: HomeAssistant, line_bot_api: LineBotApi, event: MessageEvent):
    text = event.message.text
    if text == 'bye':
        exit_chat(line_bot_api, event)
        return

    hass.bus.fire(EVENT_WEBHOOK_TEXT_RECEIVED, {
        'reply_token': event.reply_token,
        'event': event.as_json_dict(),
        'content': event.message.as_json_dict(),
        'text': event.message.text
    })

@HANDLERS.register("PostbackEvent")
def handle_message(hass: HomeAssistant, line_bot_api: LineBotApi, event: PostbackEvent):
    hass.bus.fire(EVENT_WEBHOOK_POSTBACK_RECEIVED, {
        'reply_token': event.reply_token,
        'event': event.as_json_dict(),
        'content': event.postback.as_json_dict(),
        'data': event.postback.data,
        'data_json': dict(parse_qsl(event.postback.data)),
        'params': event.postback.params
    })

def exit_chat(line_bot_api: LineBotApi, event: MessageEvent):
    if isinstance(event.source, SourceGroup):
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='Leaving group'))
        line_bot_api.leave_group(event.source.group_id)
    elif isinstance(event.source, SourceRoom):
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='Leaving group'))
        line_bot_api.leave_room(event.source.room_id)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Bot can't leave from 1:1 chat"))
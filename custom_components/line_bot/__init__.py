import logging
import requests
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_TOKEN
from urllib.parse import urlencode

DOMAIN = 'line_bot'
_LOGGER = logging.getLogger(__name__)
LINE_API_URL = "https://api.line.me/v2/bot/message/push"
ALLOWED_CHAT_IDS = "allowed_chat_ids"

TYPE = "type"
MESSAGE_TYPE_TEXT = "text"
MESSAGE_TYPE_STICKER = "sticker"
MESSAGE_TYPE_IMAGE = "image"
MESSAGE_TYPE_VIDEO = "video"
MESSAGE_TYPE_AUDIO = "audio"
MESSAGE_TYPE_LOCATION = "location"
MESSAGE_TYPE_TEMPLATE = "template"
TEMPLATE_TYPE_BUTTON = "buttons"
TEMPLATE_TYPE_CONFIRM = "confirm"
TO = "to"

def setup(hass, config):
    lineClient = LineNotificationService(config[DOMAIN].get(CONF_TOKEN), config[DOMAIN].get(ALLOWED_CHAT_IDS))

    def send_raw_message(call):
        payload = {**call.data}
        lineClient.send(payload)
    def send_text_message(call):
        lineClient.send({"to": call.data.get(TO), "messages": [TextMessage(call.data.get("message")).get()]})
    def send_sticker_message(call):
        lineClient.send({"to": call.data.get(TO), "messages": [StickerMessage(call.data.get("packageId"), call.data.get("stickerId")).get()]})
    def send_image_message(call):
        url = call.data.get("url")
        preview_url = call.data.get("preview_url", url)
        lineClient.send({"to": call.data.get(TO), "messages": [ImageMessage(url, preview_url).get()]})
    def send_video_message(call):
        url = call.data.get("url")
        preview_url = call.data.get("preview_url", url)
        lineClient.send({"to": call.data.get(TO), "messages": [VideoMessage(url, preview_url).get()]})
    def send_audio_message(call):
        url = call.data.get("url")
        duration = call.data.get("duration")
        lineClient.send({"to": call.data.get(TO), "messages": [AudioMessage(url, duration).get()]})
    def send_location_message(call):
        title = call.data.get("title", "unknown")
        address = call.data.get("address", "unknown")
        latitude = call.data.get("latitude")
        longitude = call.data.get("longitude")
        lineClient.send({"to": call.data.get(TO), "messages": [LocationMessage(title, address, latitude, longitude).get()]})

    def send_button_message(call):
        message = call.data.get("message")
        altText = call.data.get("altText", message)
        buttons = call.data.get("buttons")
        buttonTemplate = ButtonTemplate(message, to_actions(buttons))
        lineClient.send({"to": call.data.get(TO), "messages": [TemplateMessage(altText, buttonTemplate).get()]})

    def send_confirm_message(call):
        message = call.data.get("message")
        altText = call.data.get("altText", message)
        buttons = call.data.get("buttons")
        confirmTemplate = ConfirmTemplate(message, to_action(buttons))
        lineClient.send({"to": call.data.get(TO), "messages": [TemplateMessage(altText, confirmTemplate).get()]})

    hass.services.register(DOMAIN, 'send_raw_message', send_raw_message)
    hass.services.register(DOMAIN, 'send_message', send_text_message)
    hass.services.register(DOMAIN, 'send_sticker', send_sticker_message)
    hass.services.register(DOMAIN, 'send_image', send_image_message)
    hass.services.register(DOMAIN, 'send_video', send_image_message)
    hass.services.register(DOMAIN, 'send_audio', send_audio_message)
    hass.services.register(DOMAIN, 'send_location', send_location_message)
    hass.services.register(DOMAIN, 'send_button', send_button_message)
    hass.services.register(DOMAIN, 'send_confirm', send_confirm_message)
    return True

class LineNotificationService:
    def __init__(self, token, allowed_chat_ids):
        """Initialize the service."""
        self._token = token
        self._allowed_chat_ids = allowed_chat_ids
        self._http_headers = {"content-type" : "application/json", "Authorization": "Bearer " + self._token}

    def send(self, payload):
        response = None
        try:
            _LOGGER.debug('payload: %s', payload)
            payload[TO] = self._allowed_chat_ids.get(payload.get(TO))
            response = requests.post(LINE_API_URL, headers=self._http_headers, timeout=10, json=payload)
            _LOGGER.debug('JSON Response: %s', response.content.decode('utf8'))
            response.raise_for_status()
        except Exception as ex:
            _LOGGER.error('Error occurred: %s', ex)
            _LOGGER.error('Failed to call Line API : %s', response.content.decode('utf8'))
            raise

def to_actions(buttons):
    actions = []
    for button in buttons:
        action = {}
        text = button.get("text")
        data = button.get("data")
        uri = button.get("uri")
        if data is not None:
            action["type"] = "postback"
            action["label"] = button.get("label", text)
            action["data"] = urlencode(data)
        elif uri is not None:
            action["type"] = "uri"
            action["label"] = button.get("label", text)
            action["uri"] = uri
        else:
            action["type"] = "message"
            action["label"] = button.get("label", text)
            action["text"] = text
        actions.append(action)
    return actions

class Message:
    def __init__(self, type, **kwargs):
        self._payload = {TYPE: type, **kwargs}
    def get(self):
        return self._payload

class TextMessage(Message):
    def __init__(self, text):
        Message.__init__(self, MESSAGE_TYPE_TEXT, text=text)

class StickerMessage(Message):
    def __init__(self, packageId, stickerId):
        Message.__init__(self, MESSAGE_TYPE_STICKER, packageId=packageId, stickerId=stickerId)

class ImageMessage(Message):
    def __init__(self, originalContentUrl, previewImageUrl):
        Message.__init__(self, MESSAGE_TYPE_IMAGE, originalContentUrl=originalContentUrl, previewImageUrl=previewImageUrl)

class VideoMessage(Message):
    def __init__(self, originalContentUrl, previewImageUrl):
        Message.__init__(self, MESSAGE_TYPE_VIDEO, originalContentUrl=originalContentUrl, previewImageUrl=previewImageUrl)

class AudioMessage(Message):
    def __init__(self, originalContentUrl, duration):
        Message.__init__(self, MESSAGE_TYPE_AUDIO, originalContentUrl=originalContentUrl, duration=duration)

class LocationMessage(Message):
    def __init__(self, title, address, latitude, longitude):
        Message.__init__(self, MESSAGE_TYPE_LOCATION, title=title, address=address, latitude=latitude, longitude=longitude)

class TemplateMessage(Message):
    def __init__(self, altText, template):
        Message.__init__(self, MESSAGE_TYPE_TEMPLATE, altText=altText, template=template)
    def get(self):
        self._payload["template"] = self._payload["template"].get()
        return self._payload

class Template:
    def __init__(self, type, **kwargs):
        self._payload = {TYPE: type, **kwargs}
    def get(self):
        return self._payload
class ButtonTemplate(Template):
    def __init__(self, text, actions, **kwargs):
        Template.__init__(self, TEMPLATE_TYPE_BUTTON, text=text, actions=actions, **kwargs)
class ConfirmTemplate(Template):
    def __init__(self, text, actions, **kwargs):
        Template.__init__(self, TEMPLATE_TYPE_CONFIRM, text=text, actions=actions)
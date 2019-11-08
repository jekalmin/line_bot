import logging
import requests
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_TOKEN

DOMAIN = 'line_bot'
_LOGGER = logging.getLogger(__name__)
LINE_API_URL = "https://api.line.me/v2/bot/message/push"
CONF_CHAT_ID = "chat_id"
ALLOWED_CHAT_IDS = "allowed_chat_ids"

TYPE = "type"
TYPE_TEXT = "text"
TYPE_STICKER = "sticker"
TYPE_IMAGE = "image"
TYPE_VIDEO = "video"
TYPE_AUDIO = "audio"
TYPE_LOCATION = "location"
TO = "to"

def setup(hass, config):
    _LOGGER.info("token: %s", config[DOMAIN].get(CONF_TOKEN))
    lineClient = LineNotificationService(config[DOMAIN].get(CONF_TOKEN), config[DOMAIN].get(ALLOWED_CHAT_IDS))

    dictget = lambda d, *k: [d[i] for i in k]

    def send_text_message(call):
        lineClient.send(call.data.get(TO), TextMessage(*dictget(call.data, "text")))
    def send_sticker_message(call):
        lineClient.send(call.data.get(TO), StickerMessage(*dictget(call.data, "packageId", "stickerId")))
    def send_image_message(call):
        lineClient.send(call.data.get(TO), ImageMessage(*dictget(call.data, "originalContentUrl", "previewImageUrl")))
    def send_video_message(call):
        lineClient.send(call.data.get(TO), VideoMessage(*dictget(call.data, "originalContentUrl", "previewImageUrl")))
    def send_audio_message(call):
        lineClient.send(call.data.get(TO), AudioMessage(*dictget(call.data, "originalContentUrl", "duration")))
    def send_location_message(call):
        lineClient.send(call.data.get(TO), LocationMessage(*dictget(call.data, "title", "address", "latitude", "longitude")))

    hass.services.register(DOMAIN, 'send_message', send_text_message)
    hass.services.register(DOMAIN, 'send_sticker', send_sticker_message)
    hass.services.register(DOMAIN, 'send_image', send_image_message)
    hass.services.register(DOMAIN, 'send_video', send_image_message)
    hass.services.register(DOMAIN, 'send_audio', send_audio_message)
    hass.services.register(DOMAIN, 'send_location', send_location_message)
    return True

class LineNotificationService:
    def __init__(self, token, allowed_chat_ids):
        """Initialize the service."""
        self._token = token
        self._allowed_chat_ids = allowed_chat_ids
        self._http_headers = {"content-type" : "application/json", "Authorization": "Bearer " + self._token}

    def send(self, to, message):
        response = None
        try:
            payload = {"to": self._allowed_chat_ids.get(to), "messages":[message.get()] }
            response = requests.post(LINE_API_URL, headers=self._http_headers, timeout=10, json=payload)
            _LOGGER.debug('JSON Response: %s', response.content.decode('utf8'))
            response.raise_for_status()
        except Exception as ex:
            _LOGGER.error('Error occurred: %s', ex)
            _LOGGER.error('Failed to call Line API : %s', response.content.decode('utf8'))
            raise

class Message:
    def __init__(self, type, **kwargs):
        self._payload = {TYPE: type, **kwargs}
    def get(self):
        return self._payload

class TextMessage(Message):
    def __init__(self, text):
        Message.__init__(self, TYPE_TEXT, text=text)

class StickerMessage(Message):
    def __init__(self, packageId, stickerId):
        Message.__init__(self, TYPE_STICKER, packageId=packageId, stickerId=stickerId)

class ImageMessage(Message):
    def __init__(self, originalContentUrl, previewImageUrl):
        Message.__init__(self, TYPE_IMAGE, originalContentUrl=originalContentUrl, previewImageUrl=previewImageUrl)

class VideoMessage(Message):
    def __init__(self, originalContentUrl, previewImageUrl):
        Message.__init__(self, TYPE_VIDEO, originalContentUrl=originalContentUrl, previewImageUrl=previewImageUrl)

class AudioMessage(Message):
    def __init__(self, originalContentUrl, duration):
        Message.__init__(self, TYPE_AUDIO, originalContentUrl=originalContentUrl, duration=duration)

class LocationMessage(Message):
    def __init__(self, title, address, latitude, longitude):
        Message.__init__(self, TYPE_LOCATION, title=title, address=address, latitude=latitude, longitude=longitude)

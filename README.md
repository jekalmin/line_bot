# HASS-Line-Bot
Home Assistant custom component for notifying message via Line Messaging API (https://developers.line.biz/en/docs/messaging-api/overview/)

## Usage
```
service: line_bot.send_message
data:
  to: me
  message:
    type: text
    text: "Hello World!"
```

## Prequisite
- Created a channel from Line Console.
    - Follow instructions from the [link](https://developers.line.biz/en/docs/messaging-api/getting-started/) to create a new channel.

## Installation

```
/custom_components/line_bot/
```
into
```
<config directory>/custom_components/line_bot/
```

## Configuration
#### Example configuration.yaml:
```yaml
line_bot:
  token: !secret line_bot_token
  secret: !secret line_bot_secret
  allowed_chat_ids:
    me: !secret line_chat_id
```
#### Configuration variables:

| key | required | default | dataType | description
| --- | --- | --- | --- | ---
| **token** | yes | | string | channel access token (to issue a channel access token, click Issue on the "Channel settings" page on the [console](https://developers.line.biz/console/).)
| **secret** | no | | string | channel secret. Only required to use webhook.
| **allowed_chat_ids** | yes | | dictionary | any name as a key, ID of target recipient as a value. Do not use the LINE ID found on LINE (see [API Documentation](https://developers.line.biz/en/reference/messaging-api/#send-push-message))

## Services
### line_bot.send_message
| service data attribute | required | dataType | description
| --- | --- | --- | ---
| **to** | no | string | name of chat ID from `allowed_chat_ids` in `configuration.yaml` file to push message.
| **reply_token** | no | string | reply_token received from webhook [event](https://developers.line.biz/en/reference/messaging-api/#message-event) to reply message.
| **message** | yes | [Message](https://developers.line.biz/en/reference/messaging-api/#message-objects) | eg. [Text message](https://developers.line.biz/en/reference/messaging-api/#text-message), [Image message](https://developers.line.biz/en/reference/messaging-api/#image-message),[Template message](https://developers.line.biz/en/reference/messaging-api/#template-messages), etc...
#### example
![a1](https://user-images.githubusercontent.com/2917984/69494729-580fc080-0f02-11ea-8231-6d0dde9bae14.png)
```yaml
service: line_bot.send_message
data:
  to: me
  message:
    type: text
    text: "Hello World!"
```

### line_bot.send_button_message

| service data attribute | required | dataType | description
| --- | --- | --- | ---
| **to** | no | string | name of chat ID from `allowed_chat_ids` in `configuration.yaml` file to push message.
| **reply_token** | no | string | reply_token received from webhook [event](https://developers.line.biz/en/reference/messaging-api/#message-event) to reply message.
| **buttons** | yes | list | a list of [Actions](https://developers.line.biz/en/reference/messaging-api/#action-objects) (max: 5)
#### example
![162292](https://user-images.githubusercontent.com/2917984/69495124-d2424400-0f06-11ea-8688-a3cc704eb73f.jpg)
```yaml
service: line_bot.send_button_message
data:
  to: me
  text: What do you want to do?
  buttons:
    # MessageAction (https://developers.line.biz/en/reference/messaging-api/#message-action)
    - label: Turn off the light
      text: light off
    # PostbackAction (https://developers.line.biz/en/reference/messaging-api/#postback-action)
    - label: Buy
      data: action=buy&itemid=111
    # UriAction (https://developers.line.biz/en/reference/messaging-api/#uri-action)
    - uri: https://www.google.com/
      label: Google
```

### line_bot.send_confirm_message

| service data attribute | required | dataType | description
| --- | --- | --- | ---
| **to** | no | string | name of chat ID from `allowed_chat_ids` in `configuration.yaml` file to push message.
| **reply_token** | no | string | reply_token received from webhook [event](https://developers.line.biz/en/reference/messaging-api/#message-event) to reply message.
| **buttons** | yes | list | a list of [Actions](https://developers.line.biz/en/reference/messaging-api/#action-objects) (max: 2)
#### example
![162289](https://user-images.githubusercontent.com/2917984/69494775-cbb1cd80-0f02-11ea-827a-74955937cc8d.jpg)
```yaml
service: line_bot.send_confirm_message
data:
  to: me
  text: Are you sure?
  buttons:
    # PostbackAction 
    - text: Yes 
      data: action=buy&itemid=111 # equivalent to {"label" : "Yes", "data" : "action=buy&itemid=111 "}
    # MessageAction
    - text: No # equivalent to {"text" : "No", "label" : "No"}
```

## Events
### line_webhook_text_received
| event data attribute | dataType | description
| --- | --- | ---
| **reply_token** | string | It is used to reply message.
| **event** | [MessageEvent](https://line-bot-sdk-python.readthedocs.io/en/stable/linebot.models.html#linebot.models.events.MessageEvent) | Event object which contains the sent message. The message field contains a message object which corresponds with the message type. You can reply to message events.
| **content** | [TextMessage](https://line-bot-sdk-python.readthedocs.io/en/stable/linebot.models.html#linebot.models.messages.TextMessage) | Message object which contains the text sent from the source.
| **text** | string | actual text received

### line_webhook_postback_received
| event data attribute | dataType | description
| --- | --- | ---
| **reply_token** | string | It is used to reply message.
| **event** | [PostbackEvent](https://line-bot-sdk-python.readthedocs.io/en/stable/linebot.models.html#linebot.models.events.PostbackEvent) | Event object for when a user performs an action on a template message which initiates a postback. You can reply to postback events.
| **content** | [Postback](https://line-bot-sdk-python.readthedocs.io/en/stable/linebot.models.html#linebot.models.events.Postback) | Postback
| **data** | string | Postback data
| **data_json** | dictionary | Postback data as JSON object
| **params** | dictionary | JSON object with the date and time selected by a user through a datetime picker action. Only returned for postback actions via the datetime picker.
# HASS-Line-Bot
Home Assistant custom component for notifying message via Line Messaging API (https://developers.line.biz/en/docs/messaging-api/overview/)

## Usage
```
service: line_bot.send_message
data:
  to: me
  message:
    type: text
    message: "Hello World!"
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
```yaml
service: line_bot.send_message
data:
  to: me
  message:
    type: text
    message: "Hello World!"
```


### line_bot.send_button_message

| service data attribute | required | dataType | description
| --- | --- | --- | ---
| **to** | no | string | name of chat ID from `allowed_chat_ids` in `configuration.yaml` file to push message.
| **reply_token** | no | string | reply_token received from webhook [event](https://developers.line.biz/en/reference/messaging-api/#message-event) to reply message.
| **text** | yes | string | any message
#### example
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
| **text** | yes | string | any message
#### example
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
# HASS-Line-Bot
Home Assistant custom component for notifying message via Line Messaging API (https://developers.line.biz/en/docs/messaging-api/overview/)

## Usage
```
service: line_bot.send_message
data:
  to: me
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
  allowed_chat_ids:
    me: !secret line_chat_id
```
#### Configuration variables:

| key | required | default | dataType | description
| --- | --- | --- | --- | ---
| **token** | yes | | string | channel access token (to issue a channel access token, click Issue on the "Channel settings" page on the [console](https://developers.line.biz/console/).)
| **allowed_chat_ids** | yes | | dictionary | any name as a key, ID of target recipient as a value. Do not use the LINE ID found on LINE (see [API Documentation](https://developers.line.biz/en/reference/messaging-api/#send-push-message))

## Services
### line_bot.send_message
| service data attribute | required | description
| --- | --- | ---
| **to** | yes | name of chat ID from `allowed_chat_ids` in `configuration.yaml` file.
| **message** | yes | message


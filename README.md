# Line Bot
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

1. Install via custom component of HACS.

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jekalmin&repository=line_bot&category=integration)
2. Go to https://developers.line.biz/console
3. Retrieve "Channel access token" and "Channel secret" from Line Console

4. Install integration
    - [Settings] > [Devices and Services] > [Add Integration] > [Line Bot]
    - Use "Channel access token" and "Channel secret" retrieved from above (#3).
        <img width="302" alt="스크린샷 2024-12-22 오후 9 00 33" src="https://github.com/user-attachments/assets/b5a8fc74-d2f7-415a-8c03-10f3fab4e46f" />


5. Set "Webhook URL" from "Messaging API" tab of Line Console as below
    - Webhook URL is base_url + "/api/line/callback"
    - Your HomeAssistant URL has to support https

    <img width="300" alt="스크린샷 2024-12-22 오후 9 13 12" src="https://github.com/user-attachments/assets/7c1de92c-e44d-492e-950a-5e11946bb5a2" />
    
   
6. Click "Verify" button to verify URL is valid. It has to return "Success"

    ![11](https://user-images.githubusercontent.com/2917984/69878717-081d6900-1309-11ea-8b08-c319bd4b333a.png)

7. Add a bot as a friend by either QR code or Bot ID
8. Send any message to a bot
9. Go to [Configure > Add a chat] and follow the directions.

    configure | add a chat | configure a chat
    --|--|--
    <img width="442" src="https://github.com/user-attachments/assets/63ddeb48-6248-4488-813a-429b8f993a85" /> | <img width="400" src="https://github.com/user-attachments/assets/20475b4b-c2d1-4ee2-bc8a-0ede595f7da7" /> | <img width="400" src="https://github.com/user-attachments/assets/f581c3c7-139a-44ec-8707-5badc4c00f4b" />

10. Try [examples](https://github.com/jekalmin/HASS-line-bot/tree/master/examples)

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
| **buttons** | yes | list | a list of [Actions](https://developers.line.biz/en/reference/messaging-api/#action-objects) (max: 4)
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
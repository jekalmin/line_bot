# Echo Bot
## Example

![1](https://user-images.githubusercontent.com/2917984/69898413-ac9cbb00-139c-11ea-9bc6-13ea64ae36e7.png)

## Prequisite
Assume you have successfully [configured](https://github.com/jekalmin/HASS-line-bot#installation) line bot webhook
## Configuration
1.  Add a following automation in your automations.yaml

    ```yaml
    - alias: on_line_webhook_text_received
      trigger:
      - event_type: line_webhook_text_received
        platform: event
      action:
      - service: line_bot.send_message
        data_template:
          reply_token: '{{ trigger.event.data.reply_token }}'
          message:
            text: '{{ trigger.event.data.text }}'
            type: text
    ```
2. Send any message via Line Messenger
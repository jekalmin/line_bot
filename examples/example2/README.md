# Postback Action Event
## Example

![2](https://user-images.githubusercontent.com/2917984/69898612-09997080-139f-11ea-81cd-78f56e92b690.png)

## Prequisite
Assume you have successfully [configured](https://github.com/jekalmin/HASS-line-bot#installation) line bot webhook
## Configuration
1.  Add a following automation in your automations.yaml

    ```yaml
    - alias: on_line_webhook_text_received_test
      trigger:
      - platform: event
        event_type: line_webhook_text_received
        event_data:
          text: test
      action:
      - service: line_bot.send_button_message
        data_template:
          reply_token: '{{ trigger.event.data.reply_token }}'
          text: '[EMERGENCY] motion detected'
          buttons:
          - text: Activate Siren
    - alias: on_line_webhook_text_received_activate_siren
      trigger:
      - platform: event
        event_type: line_webhook_text_received
        event_data:
          text: Activate Siren
      action:
      - service: line_bot.send_confirm_message
        data_template:
          reply_token: '{{ trigger.event.data.reply_token }}'
          text: 'Are you sure?'
          buttons:
          - text: Yes
            data: entity=siren&action=on
          - text: No
            data: nothing
    - alias: on_line_webhook_postback_received_siren
      trigger:
      - platform: event
        event_type: line_webhook_postback_received
        event_data:
          entity: siren
          action: on
      action:
      - service: line_bot.send_message
        data_template:
          reply_token: '{{ trigger.event.data.reply_token }}'
          message:
            text: Sirens Activated!
            type: text
    ```
2. Send message "test" via Line Messenger
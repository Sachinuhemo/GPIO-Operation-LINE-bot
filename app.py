import RPi.GPIO as GPIO
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

app = Flask(__name__)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
configuration = Configuration(access_token=linechannel.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(linechannel.LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        rpm = event.message.text

        if rpm.isdigit() and 2 <= float(rpm) <= 27 and not float(rpm) in [14, 15]:
            GPIO.setup(int(rpm), GPIO.OUT)
            output_value = GPIO.input(int(rpm))
            if output_value == 0:
                GPIO.output(int(rpm), True)
                sem = f'GPIO{rpm} Teue'
            else:
                GPIO.output(int(rpm), False)
                sem = f'GPIO{rpm} False'

            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=sem)]
                )
            )
    
if __name__ == "__main__":
    app.run()

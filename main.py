from flask import Flask, request, abort
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,JoinEvent
)

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

#環境変数取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.source.type == "user":
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text=event.message.text))

@handler.add(JoinEvent)
def handle_join(event):
    group_id = event.source.group_id
    s = set()
    if os.path.exists('data/data.txt'):
        with open('data/data.txt', mode='r') as f:
            s = set(line.rstrip('\n') for line in f.readlines())
    s.add(group_id)
    with open('data/data.txt', mode='w') as f:
        f.write('\n'.join(s))

    line_bot_api.push_message(
        group_id,
        TextSendMessage(text="体温を入力してね\nhttps://docs.google.com/spreadsheets/d/1ZrHi9Yt2w1X1oIgyvl01tBdaH7SlUwgu3UGTtRX8aAA/edit?usp=sharing")
    )

if __name__ == "__main__":
    # app.run()
    port = 5000
    app.run(host="0.0.0.0", port=port)
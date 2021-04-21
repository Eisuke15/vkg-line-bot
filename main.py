import os

from dotenv import load_dotenv
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (JoinEvent, LeaveEvent, MessageEvent, TextMessage,
                            TextSendMessage)

from models import Base, Session, engine
from models.models import Group_id

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

    Base.metadata.create_all(bind=engine)
    session = Session()
    session.add(Group_id(group_id))
    session.commit()
    session.close()

    # pushText = TextSendMessage(text="追加ありがとうございます。")
    # line_bot_api.push_message(to=group_id,messages=pushText)

@handler.add(LeaveEvent)
def handle_leave(event):
    group_id = event.source.group_id

    Base.metadata.create_all(bind=engine)
    session = Session()
    session.query(Group_id).filter(Group_id.g_id == group_id).delete()
    session.commit()
    session.close()

import os

from dotenv import load_dotenv
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (JoinEvent, LeaveEvent, MessageEvent, TextMessage,
                            TextSendMessage)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, Group_id

load_dotenv()

app = Flask(__name__)

#Flaskのconfig設定
app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]

#Lineのアクセストークン、アクセスキー取得
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

#DB用初期設定
engine = create_engine(os.environ["DB_URL"], convert_unicode=True)
Session = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base.metadata.create_all(bind=engine)

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

    session = Session()
    session.add(Group_id(group_id))
    session.commit()
    session.close()

    # pushText = TextSendMessage(text="追加ありがとうございます。")
    # line_bot_api.push_message(to=group_id,messages=pushText)

@handler.add(LeaveEvent)
def handle_leave(event):
    group_id = event.source.group_id

    session = Session()
    session.query(Group_id).filter(Group_id.g_id == group_id).delete()
    session.commit()
    session.close()

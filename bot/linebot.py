import os

from flask import Blueprint

from linebot import LineBotApi, WebhookHandler
from linebot.models import (JoinEvent, LeaveEvent, MessageEvent, TextMessage,
                            TextSendMessage)

from .models import Session, Group

bp = Blueprint('linebot', __name__)

#Lineのアクセストークン、アクセスキー取得
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

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
    session.add(Group(group_id))
    session.commit()
    session.close()

    # pushText = TextSendMessage(text="追加ありがとうございます。")
    # line_bot_api.push_message(to=group_id,messages=pushText)

@handler.add(LeaveEvent)
def handle_leave(event):
    group_id = event.source.group_id

    session = Session()
    session.query(Group).filter(Group.group_id == group_id).delete()
    session.commit()
    session.close()

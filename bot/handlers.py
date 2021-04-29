from flask import Blueprint
from linebot import LineBotApi, WebhookHandler
from linebot.models import (JoinEvent, LeaveEvent, MessageEvent, TextMessage,
                            TextSendMessage)

from .db import db
from .environment import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from .models import Cancellation, Group

bp = Blueprint('handlers', __name__)

#Lineのアクセストークン、アクセスキー取得
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.source.type == "user":
        text = event.message.text
        if text.startswith("/cancel"):
            sendmessage = parse_cancel(text)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=sendmessage)
                )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text))

@handler.add(JoinEvent)
def handle_join(event):
    group_id = event.source.group_id

    db.session.add(Group(group_id=group_id))
    db.session.commit()

@handler.add(LeaveEvent)
def handle_leave(event):
    group_id = event.source.group_id

    option = Group.query.filter_by(group_id=group_id)
    if option.count() > 0:
        db.session.delete(Group.query.filter_by(group_id=group_id))
        db.session.commit()

def parse_cancel(text):
    texts = text.split('\n')
    command = texts[0].split()
    if len(texts) == 1 and command[1] == "list":
        cancellations = list(map(str, Cancellation.query.all()))
        return "no cancellation" if len(cancellations) == 0 else'\n'.join(cancellations)

    elif len(texts) > 1 and texts[1].isdigit():
        day_of_the_week = int(texts[1])

        if len(command) == 1:
            db.session.add(Cancellation(day_of_the_week=day_of_the_week))
            db.session.commit()
            return "created cancellation\nday_of_the_week={}".format(day_of_the_week)

        elif command[1] == "delete":
            option = Cancellation.query.filter_by(day_of_the_week=day_of_the_week)
            if option.count() == 0:
                return "Cancellation whose day_of_the_week={} does not exists.".format(day_of_the_week)
            else:
                db.session.delete(option.first())
                db.session.commit()
                return "deleted cancellation\nday_of_the_week={}".format(day_of_the_week)
            
    return "usage:\n/cancel [-a | -d]\nday_of_the_week[0~6]"
        

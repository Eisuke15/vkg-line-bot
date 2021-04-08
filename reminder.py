import datetime
import os

import pytz
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from models import Base, Session, engine
from models.models import Group_id

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

remindtext = """\
体温を入力してね
https://docs.google.com/spreadsheets/d/1ZrHi9Yt2w1X1oIgyvl01tBdaH7SlUwgu3UGTtRX8aAA/edit?usp=sharing
"""

def main():
    if datetime.datetime.now(pytz.timezone('Asia/Tokyo')).weekday() in [1,3,4,5,6] :
        pushText = TextSendMessage(text=remindtext)
        session = Session()
        groups = session.query(Group_id)
        for group in groups:
            line_bot_api.push_message(to=group.g_id,messages=pushText)
        session.close()

if __name__ == "__main__":
    main()

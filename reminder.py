import os
import datetime
import pytz

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from dotenv import load_dotenv
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
    if datetime.datetime.now(pytz.timezone('Asia/Tokyo')).weekday() in [1,3,4,5,6] and os.path.exists(data/data.txt):
        with open("data/data.txt") as f:
            groups = [line.rstrip('\n') for line in f.readlines()]
        pushText = TextSendMessage(text=remindtext)
        for group in groups:
            line_bot_api.push_message(to=group,messages=pushText)

if __name__ == "__main__":
    main()
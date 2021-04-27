import datetime
import os
import sys

import pytz
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from bot import Session, handler, line_bot_api
from bot.models import Group

load_dotenv()

def main(week):
    if datetime.datetime.now(pytz.timezone('Asia/Tokyo')).weekday() in week:
        remindtext = "体温を入力してね" + "\n" + os.environ["SPREADSHEET_URL"]
        pushText = TextSendMessage(text=remindtext)
        session = Session()
        groups = session.query(Group)
        for group in groups:
            line_bot_api.push_message(to=group.group_id,messages=pushText)
        session.close()

if __name__ == "__main__":
    #曜日を指定する数字列をコマンドライン引数にとる。0~6で日~土
    week = list(map(int,sys.argv[1:]))
    main(week)

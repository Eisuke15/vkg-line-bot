import os

from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler

"""
環境変数、その他多くのファイルから呼び出される変数はまとめてここで定義しておく。
"""

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
SPREADSHEET_URL = os.environ["SPREADSHEET_URL"]
SECRET_KEY = os.environ["SECRET_KEY"]
DB_URL = os.environ["DB_URL"]

# Line API
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Database
db = SQLAlchemy()

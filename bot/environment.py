"""環境変数を読み込む。

その他多くのファイルから呼び出されるオブジェクトもついでにまとめてここで定義しておく。
"""

import os

import gspread
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler

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

# gspread credential
credentials = {
    "type": "service_account",
    "project_id": os.environ["GSPREAD_PROJECT_ID"],
    "private_key_id": os.environ["GSPREAD_PRIVATE_KEY_ID"],
    "private_key": os.environ["GSPREAD_PRIVATE_KEY"],
    "client_email": os.environ["GSPREAD_CLIENT_EMAIL"],
    "client_id": os.environ["GSPREAD_CLIENT_ID"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ["GSPREAD_CLIENT_X509_CERT_URI"],
}

# google spreadsheet 認証
gc = gspread.service_account_from_dict(credentials)
ws = gc.open_by_key(os.environ["SPREADSHEET_KEY"]).sheet1

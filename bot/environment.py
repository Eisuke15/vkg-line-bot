from dotenv import load_dotenv
import os

load_dotenv()
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
SPREADSHEET_URL = os.environ["SPREADSHEET_URL"]
SECRET_KEY = os.environ["SECRET_KEY"]
DB_URL = os.environ["DB_URL"]

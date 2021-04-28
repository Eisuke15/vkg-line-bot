import os

from dotenv import load_dotenv
from flask import Flask, request, abort

from .linebot import bp, handler
from .models import Base, engine
from linebot.exceptions import InvalidSignatureError

#環境変数ファイルから読み込み
load_dotenv()

app = Flask(__name__)

#Flaskのconfig設定
app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # テーブル作成
    Base.metadata.create_all(bind=engine)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

app.register_blueprint(bp)

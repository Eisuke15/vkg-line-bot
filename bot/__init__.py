import os

import pytz
from dotenv import load_dotenv
from flask import Flask, abort, request
from flask_migrate import Migrate

from linebot.exceptions import InvalidSignatureError

from .db import db
from . import handlers, reminder


def create_app():
    #環境変数ファイルから読み込み
    load_dotenv()

    #Flaskインスタンス
    app = Flask(__name__)

    #Flaskの初期設定
    app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DB_URL"]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    reminder.scheduler.init_app(app)
    reminder.scheduler.scheduler.configure(timezone=pytz.timezone('Asia/Tokyo'))
    db.init_app(app)
    Migrate(app, db)

    reminder.scheduler.start()

    @app.route("/callback", methods=['POST'])
    def callback():
        # get X-Line-Signature header value
        signature = request.headers['X-Line-Signature']

        # get request body as text
        body = request.get_data(as_text=True)
        app.logger.info("Request body: " + body)

        # handle webhook body
        try:
            handlers.handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return 'OK'

    app.register_blueprint(handlers.bp)
    app.register_blueprint(reminder.bp)

    return app

app = create_app()

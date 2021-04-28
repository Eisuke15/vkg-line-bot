import os

import pytz
from dotenv import load_dotenv
from flask import Flask, abort, request
from flask_apscheduler import APScheduler
from flask_migrate import Migrate

from linebot.exceptions import InvalidSignatureError

from .db import db
from .handlers import bp, handler


def create_app():
    #環境変数ファイルから読み込み
    load_dotenv()

    #Flaskインスタンス
    app = Flask(__name__)
    scheduler = APScheduler()

    #Flaskの初期設定
    app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DB_URL"]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    scheduler.init_app(app)
    scheduler.scheduler.configure(timezone=pytz.timezone('Asia/Tokyo'))
    db.init_app(app)
    Migrate(app, db)

    scheduler.start()

    @app.route("/callback", methods=['POST'])
    def callback():
        # get X-Line-Signature header value
        signature = request.headers['X-Line-Signature']

        # get request body as text
        body = request.get_data(as_text=True)
        app.logger.info("Request body: " + body)

        # handle webhook body
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return 'OK'

    @scheduler.task(
        "cron",
        id="reminder",
        hour="6,1"
    )
    def task1():
        """Sample task 1.
        Added when app starts.
        """
        print("running task 1!")

    app.register_blueprint(bp)

    return app

app = create_app()

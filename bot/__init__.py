import logging

from flask import Flask, abort, request
from flask_migrate import Migrate
from linebot.exceptions import InvalidSignatureError

from .environment import DB_URL, SECRET_KEY, db, handler
from .handlers import bp
from .reminder import start_scheduler


def create_app():

    # Flaskインスタンス
    app = Flask(__name__)

    # Flaskの初期設定
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if not app.debug:
        # loggerをgunicornのものにつけかえる。
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    # db読み込み
    db.init_app(app)
    Migrate(app, db)

    # スケジューラ開始
    start_scheduler(app)

    # 青写真読み込み
    app.register_blueprint(bp)

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

    return app


app = create_app()

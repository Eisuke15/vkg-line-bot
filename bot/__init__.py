import logging

from flask import Flask
from flask_migrate import Migrate

from .environment import DB_URL, SECRET_KEY, db
from .handlers import bp
from .reminder import start_scheduler


def create_app():

    # Flaskインスタンス
    app = Flask(__name__)

    # Flaskの初期設定
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 本番環境のみ、loggerをgunicornのものにつけかえる。
    if __name__ != '__main__':
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

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

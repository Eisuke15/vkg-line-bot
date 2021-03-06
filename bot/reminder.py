"""体温計測をリマインドする。

Flask-Schedulerを用いて、定期的に実行するタスクを定義する。
デコレータによってこの関数を実行する日時、時刻を設定できる。
大きな要素を指定すると、それ以下の要素は自動的に0に指定される。
例: `hour=6` とすると、`minute=0`, `second=0`とみなされ、毎日朝6時に実行される。
"""

from datetime import datetime

import pytz
import requests
from flask_apscheduler import APScheduler
from linebot.models import TextSendMessage

from .environment import SPREADSHEET_URL, db, line_bot_api
from .models import Cancellation, Group


def start_scheduler(app):
    """スケジューラを起動する。

    起動、アプリの初期化、タスクの定義はこの中で行う。

    Args:
        app (Flask): flaskアプリケーション
    """

    scheduler = APScheduler()
    timezone = pytz.timezone('Asia/Tokyo')
    scheduler.init_app(app)
    scheduler.scheduler.configure(timezone=timezone)
    scheduler.start()

    @scheduler.task(
        "cron",
        id="reminder",
        day_of_week="sun,thu,sat",
        hour=6,
    )
    def reminder():
        """体温計測をリマインドする。

        曜日、時間をトリガーとして設定している。

        Todo:
            曜日、時間も何らかのコマンドによってLINE上で設定できるようにする。
        """

        # DBとの接続の関係で、appの設定情報を明示的に読み込む必要がある。
        with app.app_context():
            todays_day = datetime.now(timezone).weekday()
            option = Cancellation.query.filter_by(day_of_the_week=todays_day).scalar()

            if option is None:
                remindtext = "体温を入力してね" + "\n" + SPREADSHEET_URL
                pushText = TextSendMessage(text=remindtext)
                for group in Group.query.all():
                    line_bot_api.push_message(to=group.group_id, messages=pushText)
                app.logger.info("reminded")
            else:
                db.session.delete(option)
                db.session.commit()
                app.logger.info("canceled")

    @scheduler.task(
        "cron",
        id="get_up_heroku",
        minute="*/20",
    )
    def get_up_heroku():
        """herokuの自動スリープを阻止する。

        herokuの無料サーバーは、30分間何のリクエストも来なければ自動的にスリープし、プロセスを終了してしまう。
        リマインダーを機能させるためには、herokuを常に起こしておく必要がある。
        そのために20分おきに自分自身に対してHTTPリクエストを発行するとともに、ログ出力のみ行うタスクを設定しておく。
        """

        with app.app_context():
            requests.get("https://vkg-line-bot.herokuapp.com/")
            app.logger.info("get up heroku!")

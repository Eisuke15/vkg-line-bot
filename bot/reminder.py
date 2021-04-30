"""体温計測をリマインドする。

Flask-Schedulerを用いて、定期的に実行するタスクを定義する。
"""

from datetime import datetime

import pytz
from flask_apscheduler import APScheduler
from linebot.models import TextSendMessage

from .environment import SPREADSHEET_URL, db, line_bot_api
from .models import Cancellation, Group


def start_scheduler(app):

    scheduler = APScheduler()
    timezone = pytz.timezone('Asia/Tokyo')
    scheduler.init_app(app)
    scheduler.scheduler.configure(timezone=timezone)
    scheduler.start()

    @scheduler.task(
        "cron",
        id="reminder",
        day_of_week="sun,tue,thu,sat",
        hour=23,
    )
    def reminder():
        """体温計測をリマインドする。

        デコレータによってこの関数を実行する日時、時刻を設定できる。
        大きな要素を指定すると、それ以下の要素は自動的に0に指定される。
        例: `hour=6` とすると、`minute=0`, `second=0`とみなされ、毎日朝6時に実行される。
        """
        with app.app_context():
            todays_day = datetime.now(timezone).weekday()
            option = Cancellation.query.filter_by(day_of_the_week=todays_day).scalar()

            if option is None:
                remindtext = "体温を入力してね" + "\n" + SPREADSHEET_URL
                pushText = TextSendMessage(text=remindtext)
                for group in Group.query.all():
                    line_bot_api.push_message(to=group.group_id, messages=pushText)
            else:
                db.session.delete(option)
                db.session.commit()


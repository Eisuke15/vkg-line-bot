"""LineBotが各Eventを受け取った時の処理を記述する。"""

from collections import Counter

from flask import Blueprint
from linebot.models import (JoinEvent, LeaveEvent, MessageEvent, TextMessage,
                            TextSendMessage)

from .environment import handler, line_bot_api, db
from .models import Cancellation, Group

bp = Blueprint('handlers', __name__)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """MessageEventの発生により呼び出される関数。

    基本的には個人からのメッセージにしか反応しない。（グループでテロを起こさないため。）
    """

    if event.source.type == "user":
        text = event.message.text
        if text.startswith("/cancel"):
            sendmessage = parse_cancel(text)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=sendmessage)
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text))


@handler.add(JoinEvent)
def handle_join(event):
    """JoinEventの発生により呼び出される関数
    botがグループに参加した際にGroupインスタンスを作成し、DBに格納する。
    """

    group_id = event.source.group_id
    option = Group.query.filter_by(group_id=group_id).scalar()
    # 重複したgroup_idを持つレコードを追加しない。
    if option is None:
        db.session.add(Group(group_id=group_id))
        db.session.commit()


@handler.add(LeaveEvent)
def handle_leave(event):
    """LeaveEventの発生により呼び出される関数
    botがグループを退出した際にDBから対象のGroupレコードを消去する
    """

    group_id = event.source.group_id
    option = Group.query.filter_by(group_id=group_id).scalar()
    # 念のため存在を確認し、存在する場合のみレコード削除。
    if option is not None:
        db.session.delete(option)
        db.session.commit()


class ParseError(Exception):
    """コマンドをパースする際のエラー

    パースができないことを表すために名前だけつけた、`Exception`のサブクラス。
    `Exception`を継承するので、初期化の際に引数としてエラーメッセージを受け取る。
    `str()`でクラスを文字列にすると、エラーメッセージを吐く。
    """


def parse_cancel(text):
    """コマンドの先頭が"/cancel"の時に呼ばれる。

    コマンド "/cancel [add | delete | list] [args]"

    Args:
        text: (str) コマンドの文全体を受け取る。

    Returns:
        str: コマンド送信者に送り返す文章

    Note:
        コマンド "/cancel [add | delete | list] [args]"
    """

    # datetime型のweekdayメソッドの返す数字をDBに格納する。入力、出力には漢字も用いるので変換テーブルを用意する。
    CONV_TABLE = {
        0: "月",
        1: "火",
        2: "水",
        3: "木",
        4: "金",
        5: "土",
        6: "日",
    }
    INV_CONV_TABLE = {v: k for k, v in CONV_TABLE.items()}

    def parse_day_of_the_week(operand):
        """曜日を表す文字列を受けとり、数字と漢字に翻訳する。

        Args:
            operand (str): コマンドの中の、曜日を示すオペランドを受け取る。

        Returns:
            int: 曜日を表す数字
            str: 曜日を表す漢字

        Raises:
            ParseError: なんらかの理由によりパースできない時に発生。
        """

        message = "月~日の一文字の漢字、または0~6の数字で曜日を指定してください。"
        if operand.isdigit():
            try:
                day_number = int(operand)
                day_kanji = CONV_TABLE[day_number]
                return day_number, day_kanji
            except KeyError:
                raise ParseError(message)
        else:
            try:
                day_number = INV_CONV_TABLE[operand]
                day_kanji = operand
                return day_number, day_kanji
            except KeyError:
                raise ParseError(message)

    command = text.split()
    usage = "usage:\n/cancel [add | delete | list] [args]"
    try:
        operator = command[1]
    except IndexError:
        return usage

    if operator == "list":
        cancellations = [c.day_of_the_week for c in Cancellation.query.all()]
        if len(cancellations) == 0:
            return "キャンセルは存在しません。"
        else:
            return "\n".join("{}曜日, {}回".format(CONV_TABLE[day], count) for day, count in Counter(cancellations).items())

    elif operator == "add":
        try:
            day_number, day_kanji = parse_day_of_the_week(command[2])
        except ParseError as e:
            return str(e)

        db.session.add(Cancellation(day_of_the_week=day_number))
        db.session.commit()
        return "{}曜日のキャンセルを作成しました。".format(day_kanji)

    elif operator == "delete":
        try:
            day_number, day_kanji = parse_day_of_the_week(command[2])
        except ParseError as e:
            return str(e)

        option = Cancellation.query.filter_by(day_of_the_week=day_number).scalar()
        if option is not None:
            db.session.delete(option)
            db.session.commit()
            return "{}曜日のキャンセル予定を消去しました。".format(day_kanji)

        else:
            return "{}曜日のキャンセルは存在しません。".format(day_kanji)

    else:
        return usage

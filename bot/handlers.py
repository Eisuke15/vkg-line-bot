"""LineBotが各Eventを受け取った時の処理を記述する。"""

from collections import Counter
from datetime import datetime

import pytz
from flask import Blueprint, abort, current_app, request
from linebot.exceptions import InvalidSignatureError
from linebot.models import (JoinEvent, LeaveEvent, MessageEvent, TextMessage,
                            TextSendMessage)
from mojimoji import zen_to_han

from .environment import db, handler, line_bot_api
from .models import Cancellation, Group, Superuser

bp = Blueprint('handlers', __name__, url_prefix="")


@bp.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    current_app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """MessageEventの発生により呼び出される関数。

    基本的には個人からのメッセージにしか反応しない。（グループでテロを起こさないため。）
    何らかのエラーが発生した時は、使用者には`error`とだけ表示して、管理者にLineで通知する。
    """

    if event.source.type == "user":
        try:
            sendmessage = parse_message(event)
        except Exception as e:
            notify_superuser(e, event)
            sendmessage = "error"
        finally:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=sendmessage)
            )


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


def parse_message(event):
    """メッセージイベントが発生した際に最初に呼ばれる関数。

    受け取った文字列の先頭を解析して各関数に処理を振り分ける。

    Args:
        event: (Event) メッセージイベントオブジェクト。中にさまざまな情報が入っている。

    Returns:
        str: 送信相手に送り返す文章
    """

    text = event.message.text
    user_id = event.source.user_id
    username = line_bot_api.get_profile(user_id).display_name
    if text.startswith("/su"):
        return parse_superuser(text, user_id)
    elif text.startswith("/cancel"):
        return parse_cancel(text)
    else:
        return parse_temperature(text, username)


def parse_superuser(text, user_id):
    """コマンドの先頭が"/su"の時に呼ばれる。

    コマンド "/su [add | delete | list] [args]"

    Args:
        text: (str) コマンドの文全体を受け取る。

    Returns:
        str: コマンド送信者に送り返す文章
    """

    command = text.split()
    usage = "usage:\n/su [add | delete | list] [args]"
    try:
        operator = command[1]
    except IndexError:
        return usage

    if operator == "list":
        superusers = [line_bot_api.get_profile(su.user_id).display_name for su in Superuser.query.all()]
        if len(superusers) == 0:
            return "管理者は存在しません。"
        else:
            return "\n".join(superusers)

    elif operator == "add":
        db.session.add(Superuser(user_id=user_id))
        db.session.commit()
        return "管理者に追加しました。"

    elif operator == "delete":
        option = Superuser.query.filter_by(user_id=user_id).scalar()
        if option is not None:
            db.session.delete(option)
            db.session.commit()
            return "管理者から削除しました"
        else:
            return "管理者ではありません。"

    else:
        return usage


def parse_cancel(text):
    """コマンドの先頭が"/cancel"の時に呼ばれる。

    コマンド "/cancel [add | delete | list] [args]"

    Args:
        text: (str) コマンドの文全体を受け取る。

    Returns:
        str: コマンド送信者に送り返す文章
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


def parse_temperature(text, username):
    """いずれのコマンドにも該当しない時呼ばれる。

    Args:
        text: (str) コマンドの文全体を受け取る。
        username: (str) ユーザーネーム

    Returns:
        str: メッセージ送信者に送り返す文章
    """

    def temp_str_to_float(text):
        """体温を表す文字列を受け取り、数値化する。

        空白、改行、タブ文字などは自動的に除去する。

        Args:
            text: (str) 文字列

        Returns:
            float: 数値化した結果

        Raises:
            ParseError: 入力文字列が数値でない時に発生
        """

        text = ''.join(text.split())
        text = zen_to_han(text)
        try:
            return float(text)
        except ValueError:
            raise ParseError("数値で入力してください。")

    def update_spreadsheet(name, temp):
        """スプレッドシートに情報を記入する。

        記入するセルの場所はこの関数内で探し出す。
        該当の場所が存在しない場合、インデックスまたはカラムを作成する。

        Args:
            name: (str) 体温を測定した人
            temp: (float) 体温
        """
        timezone = pytz.timezone('Asia/Tokyo')
        now = datetime.now(timezone)
        today = str(now.date())

        # 記入先のワークシート
        from .environment import sh

        # 名前のインデックス、日付のカラムを取得
        names = sh.col_values(1)
        days = sh.row_values(1)

        # 日付の該当する列を探し出す。存在しない場合は一番右に作成
        if days[-1] == today:
            col = len(days)
        else:
            col = len(days) + 1
            sh.update_cell(1, col, today)

        # 名前の該当する行を探し出す。存在しない場合は一番下に作成
        try:
            row = names.index(name) + 1
        except ValueError:
            row = len(names) + 1
            sh.update_cell(row, 1, name)

        # セルをアップデート
        sh.update_cell(row, col, temp)

    try:
        temp = temp_str_to_float(text)
    except ParseError as e:
        return str(e)
    else:
        update_spreadsheet(username, temp)
        return "記入しました"


def notify_superuser(e, event):
    """ エラーを管理者へ通知する。

    Args:
        e: (Exception) 例外本体
        event: (Event) Webhookイベント
    """

    # ログに出力
    current_app.logger.info(str(e))

    # イベント内容を取得
    text = event.message.text
    user_id = event.source.user_id
    username = line_bot_api.get_profile(user_id).display_name

    # 管理者に内容を通知
    remindtext = "エラー発生\nusername: {}\nmessage: {}\nerror: {}".format(username, text, str(e))
    pushText = TextSendMessage(text=remindtext)
    for user in Superuser.query.all():
        line_bot_api.push_message(to=user.user_id, messages=pushText)

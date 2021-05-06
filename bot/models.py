"""DBに格納するためのモデルを定義する。"""

from .environment import db


class Superuser(db.Model):
    """管理者ユーザーのIDを格納するクラス。

    Attributes:
        id (int): テーブル内での主キー。user_idとは関係ない。
        user_id (str): 格納したいユーザのユーザid。
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)

    def __repr__(self):
        return str(self.user_id)


class Group(db.Model):
    """参加したグループのIDを格納するクラス。

    Attributes:
        id (int): テーブル内での主キー。group_idとは関係ない。
        group_id (str): 格納したいグループのグループid。
    """

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String, nullable=False)

    def __repr__(self):
        return str(self.group_id)


class Cancellation(db.Model):
    """リマインダーのキャンセル予定を格納するクラス。

    Attributes:
        id (int): テーブル内での主キー。
        day_of_the_week (int): キャンセル予定の曜日を表す数字。

    Notes:
        day_of_the_weekの曜日と数字の対応関係は、`datetime`モジュール`datetime`オブジェクトの`weeekday()`メソッドに従う。
    """

    id = db.Column(db.Integer, primary_key=True)
    day_of_the_week = db.Column(db.Integer)

    def __repr__(self):
        return str(self.day_of_the_week)

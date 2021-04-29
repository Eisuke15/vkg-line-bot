from .environment import db


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String)

    def __repr__(self):
        return str(self.group_id)


class Cancellation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_of_the_week = db.Column(db.Integer)

    def __repr__(self):
        return str(self.day_of_the_week)

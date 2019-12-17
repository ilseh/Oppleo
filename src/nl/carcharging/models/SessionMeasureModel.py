import datetime

from marshmallow import fields, Schema

from . import db


class SessionMeasureModel(db.Model):
    """
    SessionMeasure Model
    """

    # table name
    __tablename__ = 'session_measures'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime)
    value = db.Column(db.Float)

    # class constructor
    def __init__(self, data):
        """
        Class constructor
        """
        self.session_id = data.get('session_id')
        self.value = data.get('value')
        self.created_at = datetime.datetime.utcnow()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_sessions_measures():
        return SessionMeasureModel.query.all()

    @staticmethod
    def get_one_session(session_id):
        return SessionMeasureModel.query.get(session_id)


    def __repr(self):
        return '<id {}>'.format(self.id)

class SessionMeasureSchema(Schema):
    """
    SessionMeasure Schema
    """
    id = fields.Int(dump_only=True)
    session_id = fields.Str(required=True)
    value = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

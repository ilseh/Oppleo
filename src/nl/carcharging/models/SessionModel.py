from marshmallow import fields, Schema
import datetime
from . import db

class SessionModel(db.Model):
    """
    Session Model
    """

    # table name
    __tablename__ = 'session'

    id = db.Column(db.Integer, primary_key=True)
    rfid = db.Column(db.String(128), nullable=False)
    start_value = db.Column(db.Float)
    end_value = db.Column(db.Float)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    # class constructor
    def __init__(self, data):
        """
        Class constructor
        """
        self.rfid = data.get('rfid')
        self.start_value = data.get('start_value')
        self.end_value = data.get('end_value')
        self.created_at = datetime.datetime.utcnow()
        self.modified_at = datetime.datetime.utcnow()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_sessions():
        return SessionModel.query.all()

    @staticmethod
    def get_one_session(id):
        return SessionModel.query.get(id)


    def __repr(self):
        return '<id {}>'.format(self.id)

class SessionSchema(Schema):
    """
    Session Schema
    """
    id = fields.Int(dump_only=True)
    rfid = fields.Str(required=True)
    start_value = fields.Float(dump_only=True)
    end_value = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)

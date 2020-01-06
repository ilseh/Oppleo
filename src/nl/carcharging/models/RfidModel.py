from datetime import datetime

from marshmallow import fields, Schema

from nl.carcharging.models.base import Base, Session
from . import db


class RfidModel(Base):
    """
    Rfid Model
    """

    # table name
    __tablename__ = 'rfid'

    rfid = db.Column(db.String(100), primary_key=True)
    allow = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)
    last_used_at = db.Column(db.DateTime)

    def __init__(self, data):
        for key in data:
            setattr(self, key, data.get(key))
        self.allow = data.get('allow', False)
        self.created_at = data.get('created_at', datetime.now())
        self.modified_at = data.get('last_used_at', datetime.now())

    def save(self):
        session = Session()
        session.add(self)
        session.commit()

    def delete(self):
        session = Session()
        session.delete(self)
        session.commit()

    @staticmethod
    def get_all():
        session = Session()
        return session.query(RfidModel).all()

    @staticmethod
    def get_one(rfid):
        session = Session()
        return session.query(RfidModel)\
            .filter(RfidModel.rfid == str(rfid)).first()

    def __repr(self):
        return '<id {}>'.format(self.rfid)

class RfidSchema(Schema):
    """
    Rfid Schema
    """
    rfid = fields.Str(required=True)
    allow = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    last_used = fields.DateTime(dump_only=True)

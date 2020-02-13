import datetime
import logging

from marshmallow import fields, Schema

from . import db
from sqlalchemy import orm
from nl.carcharging.models.base import Base, DbSession


class ChargerConfigModel(Base):
    __tablename__ = 'charger_config'

    charger_name = db.Column(db.String(100), primary_key=True)
    charger_tariff = db.Column(db.Float)        # €/kWh
    modified_at = db.Column(db.DateTime)        # Last config update

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.models.ChargerConfigModel')
        self.logger.debug('Initializing ChargerConfigModel without data')

    # sqlalchemy calls __new__ not __init__ on reconstructing from database. Decorator to call this method
    @orm.reconstructor   
    def init_on_load(self):
        self.__init__()

    def set(self, data):
        for key in data:
            setattr(self, key, data.get(key))
        self.modified_at = datetime.datetime.now()

    def save(self):
        db_session = DbSession()
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session = DbSession()
        db_session.delete(self)
        db_session.commit()

    @staticmethod
    def get_config():
        db_session = DbSession()
        # Should be only one, return last modified
        return db_session.query(ChargerConfigModel) \
            .order_by(ChargerConfigModel.modified_at.desc()).first()

    def __repr(self):
        return self.to_str()

    def to_str(self):
        return ({
                "charger_name": str(self.charger_name),
                "charger_tariff": self.charger_tariff,
                "modified_at": (str(self.modified_at.strftime("%d/%m/%Y, %H:%M:%S")) if self.modified_at is not None else None)
            }
        )

class ChargerConfigSchema(Schema):
    """
    ChargerConfigModel Schema
    """
    charger_name = fields.Float(required=True)
    charger_tariff = fields.Float(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)


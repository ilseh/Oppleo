import datetime
import logging

from marshmallow import fields, Schema

from sqlalchemy import orm, Column, String, Float, DateTime
from nl.carcharging.models.Base import Base, DbSession


class ChargerConfigModel(Base):
    __tablename__ = 'charger_config'

    charger_name = Column(String(100), primary_key=True)
    charger_tariff = Column(Float)        # €/kWh
    modified_at = Column(DateTime)        # Last config update

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
        try:
            db_session.add(self)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            self.logger.error("Could not commit to {} table in database".format(self.__tablename__ ), exc_info=True)


    def delete(self):
        db_session = DbSession()
        try:
            db_session.delete(self)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            self.logger.error("Could not delete from {} table in database".format(self.__tablename__ ), exc_info=True)


    @staticmethod
    def get_config():
        db_session = DbSession()
        ccm = None
        try:
            # Should be only one, return last modified
            ccm = db_session.query(ChargerConfigModel) \
                            .order_by(ChargerConfigModel.modified_at.desc()) \
                            .first()
        except Exception as e:
            # Nothing to roll back
            self.logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
        return ccm


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


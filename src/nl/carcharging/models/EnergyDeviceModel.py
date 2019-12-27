from marshmallow import fields, Schema
import datetime
from . import db
from sqlalchemy import func
from nl.carcharging.models.base import Base, Session

session = Session()


class EnergyDeviceModel(Base):
    """
    EnergyDevice Model
    """

    # table name
    __tablename__ = 'energy_device'

    energy_device_id = db.Column(db.String(100), primary_key=True)

    # class constructor
    def __init__(self, data):
        """
        Class constructor
        """
        self.energy_device_id = data.get('energy_device_id')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return session.query(EnergyDeviceModel).all()

    @staticmethod
    def get_one(energy_device_id):
        return session.query.filter(EnergyDeviceModel.energy_device_id == energy_device_id)

    def __repr(self):
        return '<id {}>'.format(self.id)

class EnergyDeviceSchema(Schema):
    """
    Session Schema
    """
    id = fields.Int(dump_only=True)
    rfid = fields.Str(required=True)
    start_value = fields.Float(dump_only=True)
    end_value = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)

from marshmallow import fields, Schema

from nl.carcharging.models.base import Base, DbSession
from . import db
from sqlalchemy import orm

class EnergyDeviceModel(Base):
    """
    EnergyDevice Model
    """

    # table name
    __tablename__ = 'energy_device'

    energy_device_id = db.Column(db.String(100), primary_key=True)
    port_name = db.Column(db.String(100))
    slave_address = db.Column(db.Integer)
    baudrate = db.Column(db.Integer)
    bytesize = db.Column(db.Integer)
    parity = db.Column(db.String(1))
    stopbits = db.Column(db.Integer)
    serial_timeout = db.Column(db.Integer)
    debug = db.Column(db.Boolean)
    mode = db.Column(db.String(10))
    close_port_after_each_call = db.Column(db.Boolean)
    modbus_timeout = db.Column(db.Integer)

    def __init__(self, data):
        self.energy_device_id = data.get('energy_device_id')

    # sqlalchemy calls __new__ not __init__ on reconstructing from database. Decorator to call this method
    @orm.reconstructor   
    def init_on_load(self):
        pass

    def save(self):
        db_session = DbSession()
        db_session.add(self)
        db_session.commit()
        db_session.remove()

    def delete(self):
        db_session = DbSession()
        db_session.delete(self)
        db_session.commit()
        db_session.remove()

    @staticmethod
    def get_all():
        db_session = DbSession()
        edm = db_session.query(EnergyDeviceModel).all()
        db_session.remove()
        return edm


    @staticmethod
    def get_one(energy_device_id):
        db_session = DbSession()
        edm =  session.query(EnergyDeviceModel)\
            .filter(EnergyDeviceModel.energy_device_id == energy_device_id).first()
        db_session.remove()
        return edm

    def __repr(self):
        return '<id {}>'.format(self.id)

class EnergyDeviceSchema(Schema):
    """
    Energy Device Schema
    """
    energy_device_id = fields.Str(required=True)
    port_name = fields.Str(dump_only=True)
    slave_address = fields.Int(dump_only=True)
    baudrate = fields.Int(dump_only=True)
    bytesize = fields.Int(dump_only=True)
    parity = fields.Str(dump_only=True)
    stopbits = fields.Int(dump_only=True)
    serial_timeout = fields.Int(dump_only=True)
    debug = fields.Bool(dump_only=True)
    mode = fields.Str(dump_only=True)
    close_port_after_each_call = fields.Bool(dump_only=True)
    modbus_timeout = fields.Int(dump_only=True)


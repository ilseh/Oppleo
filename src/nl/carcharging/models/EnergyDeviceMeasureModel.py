import datetime

from marshmallow import fields, Schema

from . import db
from nl.carcharging.models.base import Base, Session

session = Session()

class EnergyDeviceMeasureModel(Base):
    """
    EnergyDeviceMeasure Model
    """

    # table name
    __tablename__ = 'energy_device_measures'

    id = db.Column(db.Integer, primary_key=True)
    energy_device_id = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime)
    kwh_l1 = db.Column(db.Float)
    kwh_l2 = db.Column(db.Float)
    kwh_l3 = db.Column(db.Float)
    a_l1 = db.Column(db.Float)
    a_l2 = db.Column(db.Float)
    a_l3 = db.Column(db.Float)
    kw_total = db.Column(db.Float)

    # class constructor
    def __init__(self, data):
        """
        Class constructor
        """
        self.energy_device_id = data.get('energy_device_id')
        self.kwh_l1 = data.get('kwh_l1')
        self.kwh_l2 = data.get('kwh_l3')
        self.kwh_l3 = data.get('kwh_l3')
        self.a_l1 = data.get('a_l1')
        self.a_l2 = data.get('a_l2')
        self.a_l3 = data.get('a_l3')
        self.kw_total = data.get('kw_total')
        self.created_at = datetime.datetime.utcnow()

    def save(self):
        session.add(self)
        session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_measures():
        return EnergyDeviceMeasureModel.query.all()

    @staticmethod
    def get_energy_device_measures(energy_device_id):
        return EnergyDeviceMeasureModel.query.filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id)


    def __repr(self):
        return '<id {}>'.format(self.id)

class EnergyDeviceMeasureSchema(Schema):
    """
    EnergyDeviceMeasure Schema
    """
    id = fields.Int(dump_only=True)
    energy_device_id = fields.Str(required=True)
    kwh_l1 = fields.Float(dump_only=True)
    kwh_l2 = fields.Float(dump_only=True)
    kwh_l2 = fields.Float(dump_only=True)
    a_l1 = fields.Float(dump_only=True)
    a_l2 = fields.Float(dump_only=True)
    a_l3 = fields.Float(dump_only=True)
    kw_total = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

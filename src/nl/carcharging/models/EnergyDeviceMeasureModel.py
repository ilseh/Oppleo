import datetime
import logging

from marshmallow import fields, Schema

from . import db
from nl.carcharging.models.base import Base, Session


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
    p_l1 = db.Column(db.Float)
    p_l2 = db.Column(db.Float)
    p_l3 = db.Column(db.Float)
    v_l1 = db.Column(db.Float)
    v_l2 = db.Column(db.Float)
    v_l3 = db.Column(db.Float)
    kw_total = db.Column(db.Float)
    hz = db.Column(db.Float)

    def __init__(self, data):
        self.logger = logging.getLogger('nl.carcharging.models.EnergyDeviceMeasureModel')

        self.logger.debug('Initializing EnergyDeviceMeasureModel with %s' % data)

        for key in data:
            setattr(self, key, data.get(key))

        self.created_at = datetime.datetime.utcnow()


    def save(self):
        session = Session()
        session.add(self)
        session.commit()

    @staticmethod
    def get_last_saved(energy_device_id):
        session = Session()
        return session.query(EnergyDeviceMeasureModel) \
            .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
            .order_by(EnergyDeviceMeasureModel.created_at.desc()).limit(1).first()

    # @staticmethod
    # def get_all_measures():
    #     return EnergyDeviceMeasureModel.query.all()
    #
    # @staticmethod
    # def get_energy_device_measures(energy_device_id):
    #     return EnergyDeviceMeasureModel.query.filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id)


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
    v_l1 = fields.Float(dump_only=True)
    v_l2 = fields.Float(dump_only=True)
    v_l3 = fields.Float(dump_only=True)
    p_l1 = fields.Float(dump_only=True)
    p_l2 = fields.Float(dump_only=True)
    p_l3 = fields.Float(dump_only=True)
    kw_total = fields.Float(dump_only=True)
    hz = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

import datetime
import logging

from marshmallow import fields, Schema

from . import db
from sqlalchemy import orm
from nl.carcharging.models.base import Base, DbSession
import json


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

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.models.EnergyDeviceMeasureModel')
        self.logger.debug('Initializing EnergyDeviceMeasureModel without data')

    # sqlalchemy calls __new__ not __init__ on reconstructing from database. Decorator to call this method
    @orm.reconstructor   
    def init_on_load(self):
        self.__init__

    def set(self, data):
        for key in data:
            setattr(self, key, data.get(key))
        # If no field created_at or it has no value, use current datetime.
        self.created_at = data.get('created_at', datetime.datetime.now())

    def save(self):
        db_session = DbSession()
        db_session.add(self)
        db_session.commit()

    def get_last_saved(self, energy_device_id):
        return self.get_last_n_saved(energy_device_id, 1)[0]

    def get_last_n_saved(self, energy_device_id, n):
        db_session = DbSession()
        edmm = db_session.query(EnergyDeviceMeasureModel) \
            .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
            .order_by(EnergyDeviceMeasureModel.created_at.desc()).limit(n).all()
        return edmm

    def get_last_n_saved_since(self, energy_device_id, since_ts, n=-1):
        db_session = DbSession()
        edmm = None
        if n == -1:
            edmm = db_session.query(EnergyDeviceMeasureModel) \
                .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                .filter(EnergyDeviceMeasureModel.created_at >= self.date_str_to_datetime(since_ts)) \
                .order_by(EnergyDeviceMeasureModel.created_at.desc()).all()
        else:
            edmm = db_session.query(EnergyDeviceMeasureModel) \
                .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                .filter(EnergyDeviceMeasureModel.created_at >= self.date_str_to_datetime(since_ts)) \
                .order_by(EnergyDeviceMeasureModel.created_at.desc()).limit(n).all()
        return edmm

    def get_created_at_str(self):
        return str(self.created_at.strftime("%d/%m/%Y, %H:%M:%S"))

    def date_str_to_datetime(self, date_time_str):
        return datetime.datetime.strptime(date_time_str, '%d/%m/%Y, %H:%M:%S')

    # @staticmethod
    # def get_all_measures():
    #     return EnergyDeviceMeasureModel.query.all()
    #
    # @staticmethod
    # def get_energy_device_measures(energy_device_id):
    #     return EnergyDeviceMeasureModel.query.filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id)

    def __repr(self):
        return '<id {}>'.format(self.id)

    # convert into JSON:
    def to_json(self):
        return (
            json.dumps({
                "energy_device_id": str(self.energy_device_id),
                "created_at": str(self.created_at.strftime("%d/%m/%Y, %H:%M:%S")),
                "kwh_l1": self.kwh_l1,
                "kwh_l2": str(self.kwh_l2),
                "kwh_l3": str(self.kwh_l3),
                "a_l1": str(self.a_l1),
                "a_l2": str(self.a_l2),
                "a_l3": str(self.a_l3),
                "p_l1": str(self.p_l1),
                "p_l2": str(self.p_l2),
                "p_l3": str(self.p_l3),
                "v_l1": str(self.v_l1),
                "v_l2": str(self.v_l2),
                "v_l3": str(self.v_l3),
                "kw_total": str(self.kw_total),
                "hz": str(self.hz)
            }
            )
        )

    def to_str(self):
        return ({
                "energy_device_id": str(self.energy_device_id),
                "created_at": str(self.created_at.strftime("%d/%m/%Y, %H:%M:%S")),
                "kwh_l1": self.kwh_l1,
                "kwh_l2": str(self.kwh_l2),
                "kwh_l3": str(self.kwh_l3),
                "a_l1": str(self.a_l1),
                "a_l2": str(self.a_l2),
                "a_l3": str(self.a_l3),
                "p_l1": str(self.p_l1),
                "p_l2": str(self.p_l2),
                "p_l3": str(self.p_l3),
                "v_l1": str(self.v_l1),
                "v_l2": str(self.v_l2),
                "v_l3": str(self.v_l3),
                "kw_total": str(self.kw_total),
                "hz": str(self.hz)
            }
        )

    # convert into dict:
    def to_dict(self):
        return ({
            "energy_device_id": str(self.energy_device_id),
            "created_at": str(self.created_at.strftime("%d/%m/%Y, %H:%M:%S")),
            "kwh_l1": self.kwh_l1,
            "kwh_l2": str(self.kwh_l2),
            "kwh_l3": str(self.kwh_l3),
            "a_l1": str(self.a_l1),
            "a_l2": str(self.a_l2),
            "a_l3": str(self.a_l3),
            "p_l1": str(self.p_l1),
            "p_l2": str(self.p_l2),
            "p_l3": str(self.p_l3),
            "v_l1": str(self.v_l1),
            "v_l2": str(self.v_l2),
            "v_l3": str(self.v_l3),
            "kw_total": str(self.kw_total),
            "hz": str(self.hz)
        }
        )


class EnergyDeviceMeasureSchema(Schema):
    """
    EnergyDeviceMeasure Schema
    """
    id = fields.Int(dump_only=True)
    energy_device_id = fields.Str(required=True)
    kwh_l1 = fields.Float(dump_only=True)
    kwh_l2 = fields.Float(dump_only=True)
    kwh_l3 = fields.Float(dump_only=True)
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

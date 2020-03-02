import datetime
import logging

from marshmallow import fields, Schema

from sqlalchemy import orm, Column, Integer, String, DateTime, Float
from nl.carcharging.models.Base import Base, DbSession
import json


class EnergyDeviceMeasureModel(Base):
    """
    EnergyDeviceMeasure Model
    """
    logger = logging.getLogger('nl.carcharging.models.EnergyDeviceMeasureModel')

    # table name
    __tablename__ = 'energy_device_measures'

    id = Column(Integer, primary_key=True)
    energy_device_id = Column(String, nullable=False)
    created_at = Column(DateTime)
    kwh_l1 = Column(Float)
    kwh_l2 = Column(Float)
    kwh_l3 = Column(Float)
    a_l1 = Column(Float)
    a_l2 = Column(Float)
    a_l3 = Column(Float)
    p_l1 = Column(Float)
    p_l2 = Column(Float)
    p_l3 = Column(Float)
    v_l1 = Column(Float)
    v_l2 = Column(Float)
    v_l3 = Column(Float)
    kw_total = Column(Float)
    hz = Column(Float)

    def __init__(self):
        pass

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
        try:
            db_session.add(self)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            self.logger.error("Could not save to {} table in database".format(self.__tablename__ ), exc_info=True)


    def get_last_saved(self, energy_device_id):
        self.logger.debug("get_last_saved() energy_device_id {} ".format(energy_device_id))
        return self.get_last_n_saved(energy_device_id, 1)[0]


    def get_last_n_saved(self, energy_device_id, n):
        db_session = DbSession()
        edmm = None
        try:
            edmm = db_session.query(EnergyDeviceMeasureModel) \
                             .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                             .order_by(EnergyDeviceMeasureModel.created_at.desc()) \
                             .limit(n) \
                             .all()
        except Exception as e:
            # Nothing to roll back
            self.logger.error("Could not save to {} table in database".format(self.__tablename__ ), exc_info=True)
        return edmm

    def get_last_n_saved_since(self, energy_device_id, since_ts, n=-1):
        db_session = DbSession()
        edmm = None
        try:
            if n == -1:
                edmm = db_session.query(EnergyDeviceMeasureModel) \
                                 .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                                 .filter(EnergyDeviceMeasureModel.created_at >= self.date_str_to_datetime(since_ts)) \
                                 .order_by(EnergyDeviceMeasureModel.created_at.desc()) \
                                 .all()
            else:
                edmm = db_session.query(EnergyDeviceMeasureModel) \
                                 .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                                 .filter(EnergyDeviceMeasureModel.created_at >= self.date_str_to_datetime(since_ts)) \
                                 .order_by(EnergyDeviceMeasureModel.created_at.desc()) \
                                 .limit(n) \
                                 .all()
        except Exception as e:
            # Nothing to roll back
            self.logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
        return edmm


    def get_usage_since(self, energy_device_id, since_ts):
        self.logger.debug("get_usage_since() energy_device_id {} since_ts {}".format(energy_device_id, str(since_ts)))
        db_session = DbSession()
        energy_at_ts = 0
        try:
            energy_at_ts = db_session.query(EnergyDeviceMeasureModel) \
                                    .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                                    .filter(EnergyDeviceMeasureModel.created_at <= since_ts) \
                                    .order_by(EnergyDeviceMeasureModel.created_at.desc()) \
                                    .first()
        except Exception as e:
            # Nothing to roll back
            self.logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
        energy_now = self.get_last_saved(energy_device_id)
        if energy_now is None or energy_at_ts is None:
            self.logger.warn('get_usage_since() - could not get data from database')
            return 0
        energy_used = round((energy_now.kw_total - energy_at_ts.kw_total) *10) /10
        self.logger.debug('get_usage_since() - since {} usage {}kWh'.format(
                    since_ts.strftime("%d/%m/%Y, %H:%M:%S"), energy_used)
                    )
        return energy_used


    # returns the created_at value at which the first time thi kwh value was measured
    @staticmethod
    def get_time_of_kwh(energy_device_id, kw_total):
        db_session = DbSession()
        edmm = None
        try:
            edmm = db_session.query(EnergyDeviceMeasureModel) \
                             .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                             .filter(EnergyDeviceMeasureModel.kw_total == kw_total) \
                             .filter(EnergyDeviceMeasureModel.a_l1 == 0) \
                             .filter(EnergyDeviceMeasureModel.a_l2 == 0) \
                             .filter(EnergyDeviceMeasureModel.a_l3 == 0) \
                             .order_by(EnergyDeviceMeasureModel.created_at.asc()) \
                             .first()
        except Exception as e:
            # Nothing to roll back
            EnergyDeviceMeasureModel.logger.error("Could not query from {} table in database".format(EnergyDeviceMeasureModel.__tablename__ ), exc_info=True)
        return edmm.created_at if edmm is not None else None 


    def get_created_at_str(self):
        return str(self.created_at.strftime("%d/%m/%Y, %H:%M:%S"))


    def date_str_to_datetime(self, date_time_str):
        return datetime.datetime.strptime(date_time_str, '%d/%m/%Y, %H:%M:%S')


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
            })
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
            })


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
        })


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

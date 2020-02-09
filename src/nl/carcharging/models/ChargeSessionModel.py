from marshmallow import fields, Schema
import datetime
import logging
from . import db
from sqlalchemy import orm
from sqlalchemy import func
from nl.carcharging.models.base import Base, DbSession
import json


class ChargeSessionModel(Base):
    """
    Charge Session Model
    """

    # table name
    __tablename__ = 'charge_session'  # -> sessions

    id = db.Column(db.Integer, primary_key=True)
    rfid = db.Column(db.String(128), nullable=False)
    energy_device_id = db.Column(db.String(128), nullable=False)
    start_value = db.Column(db.Float)
    end_value = db.Column(db.Float)
    start_time = db.Column(db.DateTime)  # was created_at
    end_time = db.Column(db.DateTime)  # was modified_at - null if session in progress
    tariff = db.Column(db.Float)  # €/kWh
    total_energy = db.Column(db.Float)  # kWh (end_value - start_value) - increasing during session
    total_price = db.Column(db.Float)  # € (total_energy * tariff) - increasing during session
    energy_device_id = db.Column(db.String(100))
    km = db.Column(db.Integer)

    # class constructor
    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.models.SessionModel')
        self.logger.debug('Initializing SessionModel without data')

    # sqlalchemy calls __new__ not __init__ on reconstructing from database. Decorator to call this method
    @orm.reconstructor
    def init_on_load(self):
        self.__init__

    def set(self, data):
        for key in data:
            if (key == 'tariff'):
                self.set_tariff(data.get(key))
            elif (key == 'total_energy'):
                self.set_total_energy(data.get(key))
            elif (key == 'total_price'):
                self.set_total_price(data.get(key))
            else:
                setattr(self, key, data.get(key))
        if self.start_time is None:
            self.start_time = datetime.datetime.now()

    def set_tariff(self, value):
        self.tariff = float(value)
        if (isinstance(self.total_energy, float)):
            self.total_price = self.total_energy * self.tariff

    def set_total_energy(self, value):
        self.total_energy = float(value)
        if (isinstance(self.tariff, float)):
            self.total_price = self.total_energy * self.tariff

    def set_total_price(self, value):
        self.total_price = float(value)
        if (isinstance(self.total_energy, float)):
            self.tariff = round(self.total_price / self.total_energy, 1)

    def save(self):
        db_session = DbSession()
        db_session.add(self)
        db_session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.modified_at = datetime.datetime.now()

        db_session = DbSession()
        db_session.commit()

    def delete(self):
        db_session = DbSession()
        db_session.delete(self)
        db_session.commit()

    @staticmethod
    def get_all_sessions():
        db_session = DbSession()
        return db_session.query(ChargeSessionModel).all()

    @staticmethod
    def get_one_charge_session(id):
        db_session = DbSession()
        try:
            return db_session.query(ChargeSessionModel) \
                .filter(ChargeSessionModel.id == id).limit(1).all()[0]
        except:
            return None

    @staticmethod
    def get_latest_charge_session(device, rfid=None):
        db_session = DbSession()
        # Build query to get id of latest chargesession for this device.
        qry_latest_id = db_session.query(func.max(ChargeSessionModel.id)).filter(ChargeSessionModel.energy_device_id ==
                                                                                 device)
        # If rfid is specified, expand the query with a filter on rfid.
        if rfid is not None:
            qry_latest_id = qry_latest_id.filter(ChargeSessionModel.rfid == str(rfid))
        #  Now query the ChargeSession that we're interested in (latest for device or latest for device AND rfid).
        latest_charge_session = db_session.query(ChargeSessionModel).filter(
            ChargeSessionModel.id == qry_latest_id).first()
        return latest_charge_session

    @staticmethod
    def get_open_charge_session_for_device(device):
        db_session = DbSession()
        # Build query to get id of latest chargesession for this device.
        open_charge_session_for_device = db_session.query(ChargeSessionModel) \
                            .filter(ChargeSessionModel.energy_device_id == device) \
                            .filter(ChargeSessionModel.end_time == None)
        return open_charge_session_for_device

    def __repr(self):
        return '<id {}>'.format(self.id)

    def get_last_n_sessions_since(self, energy_device_id=None, since_ts=None, n=-1):
        db_session = DbSession()
        if (n == -1):
            if (since_ts == None):
                if (energy_device_id == None):
                    return db_session.query(ChargeSessionModel) \
                        .order_by(ChargeSessionModel.start_time.desc()).all()
                else:  # filter energy_device_id
                    return db_session.query(ChargeSessionModel) \
                        .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                        .order_by(ChargeSessionModel.start_time.desc()).all()
            else:  # filter since_ts
                if (energy_device_id == None):
                    return db_session.query(ChargeSessionModel) \
                        .filter(ChargeSessionModel.start_time >= self.date_str_to_datetime(since_ts)) \
                        .order_by(ChargeSessionModel.start_time.desc()).all()
                else:  # filter energy_device_id
                    return db_session.query(ChargeSessionModel) \
                        .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                        .filter(ChargeSessionModel.start_time >= self.date_str_to_datetime(since_ts)) \
                        .order_by(ChargeSessionModel.start_time.desc()).all()
        else:  # limit n
            if (since_ts == None):
                if (energy_device_id == None):
                    return db_session.query(ChargeSessionModel) \
                        .order_by(ChargeSessionModel.start_time.desc()).limit(n).all()
                else:  # filter energy_device_id
                    return db_session.query(ChargeSessionModel) \
                        .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                        .order_by(ChargeSessionModel.start_time.desc()).limit(n).all()
            else:  # filter since_ts
                if (energy_device_id == None):
                    return db_session.query(ChargeSessionModel) \
                        .filter(ChargeSessionModel.start_time >= self.date_str_to_datetime(since_ts)) \
                        .order_by(ChargeSessionModel.start_time.desc()).limit(n).all()
                else:  # filter energy_device_id
                    return db_session.query(ChargeSessionModel) \
                        .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                        .filter(ChargeSessionModel.start_time >= self.date_str_to_datetime(since_ts)) \
                        .order_by(ChargeSessionModel.start_time.desc()).limit(n).all()

    def date_str_to_datetime(self, date_time_str):
        return datetime.datetime.strptime(date_time_str, '%d/%m/%Y, %H:%M:%S')

    # convert into JSON:
    def to_json(self):
        return (
            json.dumps({
                "id": str(self.id),
                "energy_device_id": str(self.energy_device_id),
                "start_time": str(self.start_time.strftime("%d/%m/%Y, %H:%M:%S")),
                "rfid": self.rfid,
                "start_value": str(self.start_value),
                "end_value": str(self.end_value),
                "tariff": str(self.tariff),
                "total_energy": str(self.total_energy),
                "total_price": str(self.total_price),
                "km": str(self.km),
                "end_time": str(self.end_time.strftime("%d/%m/%Y, %H:%M:%S"))
            })
        )

    # convert into JSON:
    def to_str(self):
        return ({
                "id": str(self.id),
                "energy_device_id": str(self.energy_device_id),
                "start_time": str(self.start_time.strftime("%d/%m/%Y, %H:%M:%S")),
                "rfid": self.rfid,
                "start_value": str(self.start_value),
                "end_value": str(self.end_value),
                "tariff": str(self.tariff),
                "total_energy": str(self.total_energy),
                "total_price": str(self.total_price),
                "km": str(self.km),
                "end_time": str(self.end_time.strftime("%d/%m/%Y, %H:%M:%S"))
            })

    # convert into dict:
    def to_dict(self):
        return ({
            "id": str(self.id),
            "energy_device_id": str(self.energy_device_id),
            "start_time": (
                str(self.start_time.strftime("%d/%m/%Y, %H:%M:%S")) if self.start_time is not None else None),
            "rfid": self.rfid,
            "start_value": str(self.start_value),
            "end_value": str(self.end_value),
            "tariff": str(self.tariff),
            "total_energy": str(self.total_energy),
            "total_price": str(self.total_price),
            "km": str(self.km),
            "end_time": (str(self.end_time.strftime("%d/%m/%Y, %H:%M:%S")) if self.end_time is not None else None)
        })


class ChargeSessionSchema(Schema):
    """
    Session Schema
    """
    id = fields.Int(dump_only=True)
    rfid = fields.Str(required=True)
    energy_device_id = fields.Str(required=True)
    start_value = fields.Float(dump_only=True)
    end_value = fields.Float(dump_only=True)
    start_time = fields.DateTime(dump_only=True)
    end_time = fields.DateTime(dump_only=True)
    tariff = fields.Float(dump_only=True)
    total_energy = fields.Float(dump_only=True)
    total_price = fields.Float(dump_only=True)
    km = fields.Integer(dump_only=True)

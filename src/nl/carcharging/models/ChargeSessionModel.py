# Return type hints https://docs.python.org/3/library/typing.html
from __future__ import annotations
import typing

from marshmallow import fields, Schema
from datetime import datetime
import logging

from sqlalchemy import orm, func, Column, Integer, String, Float, DateTime
from nl.carcharging.models.Base import Base, DbSession
import json


class ChargeSessionModel(Base):
    """
    Charge Session Model
    """

    # table name
    __tablename__ = 'charge_session'  # -> sessions

    id = Column(Integer, primary_key=True)
    rfid = Column(String(128), nullable=False)
    energy_device_id = Column(String(128), nullable=False)
    start_value = Column(Float)
    end_value = Column(Float)
    start_time = Column(DateTime)  # was created_at
    end_time = Column(DateTime)  # was modified_at - null if session in progress
    tariff = Column(Float)  # €/kWh
    total_energy = Column(Float)  # kWh (end_value - start_value) - increasing during session
    total_price = Column(Float)  # € (total_energy * tariff) - increasing during session
    energy_device_id = Column(String(100))
    km = Column(Integer)
    trigger = Column(String(12))

    TRIGGER_RFID = 'RFID'   # Manually by offering an RFID tag
    TRIGGER_AUTO = 'AUTO'   # By auto-session detection
    TRIGGER_WEB = 'WEB'     # Through the WebApp

    # class constructor
    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.models.ChargeSessionModel')


    # sqlalchemy calls __new__ not __init__ on reconstructing from database. Decorator to call this method
    @orm.reconstructor
    def init_on_load(self):
        self.__init__


    def set(self, data):
        for key in data:
            setattr(self, key, data.get(key))
        if self.start_time is None:
            self.start_time = datetime.now()


    def save(self) -> None:
        db_session = DbSession()
        try:
            db_session.add(self)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            self.logger.error("Could not save to {} table in database".format(self.__tablename__ ), exc_info=True)


    def update(self, data) -> None:
        for key, item in data.items():
            setattr(self, key, item)
        self.modified_at = datetime.now()
        db_session = DbSession()
        try:
            db_session.add(self)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            self.logger.error("Could not save to {} table in database".format(self.__tablename__ ), exc_info=True)


    def delete(self) -> None:
        db_session = DbSession()
        try:
            db_session.delete(self)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            self.logger.error("Could not delete from {} table in database".format(self.__tablename__ ), exc_info=True)


    @staticmethod
    def get_all_sessions() -> typing.List[ChargeSessionModel]:
        db_session = DbSession()
        csm = None
        try:
            csm = db_session.query(ChargeSessionModel) \
                            .all()
        except Exception as e:
            # Nothing to roll back
            self.logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
        return csm


    @staticmethod
    def get_one_charge_session(id) -> ChargeSessionModel:
        db_session = DbSession()
        csm = None
        try:
            csm = db_session.query(ChargeSessionModel) \
                            .filter(ChargeSessionModel.id == id) \
                            .limit(1) \
                            .all()[0]
        except:
            return None
        return csm

    """
    Returns session with specific values, used for condensing charge sessions
    """
    @staticmethod
    def get_specific_charge_session(energy_device_id, rfid, km, end_value, tariff) -> ChargeSessionModel:
        db_session = DbSession()
        csm = None
        try:
            csm = db_session.query(ChargeSessionModel) \
                            .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                            .filter(ChargeSessionModel.rfid == rfid) \
                            .filter(ChargeSessionModel.km == km) \
                            .filter(ChargeSessionModel.end_value == end_value) \
                            .filter(ChargeSessionModel.end_time != None) \
                            .filter(ChargeSessionModel.tariff == tariff) \
                            .first()
        except:
            return None
        return csm

    """
    Condenses two charge sessions
    """
    @staticmethod
    def condense_charge_sessions(closed_charge_session, new_charge_session) -> None:
        # energy_device_id, rfid, tariff, km are equal. Keep the end_value
        new_charge_session.start_value = closed_charge_session.start_value
        new_charge_session.start_time = closed_charge_session.start_time
        new_charge_session.trigger = closed_charge_session.trigger
        # Update totals
        new_charge_session.total_energy = new_charge_session.end_value - new_charge_session.start_value
        new_charge_session.total_price = new_charge_session.total_energy * new_charge_session.tariff
        # Save it
        new_charge_session.save()
        # Delete the old one
        closed_charge_session.delete()


    @staticmethod
    def get_latest_charge_session(device, rfid=None) -> ChargeSessionModel:
        db_session = DbSession()
        # Build query to get id of latest chargesession for this device.
        qry_latest_id = db_session.query(func.max(ChargeSessionModel.id)).filter(ChargeSessionModel.energy_device_id ==
                                                                                 device)
        # If rfid is specified, expand the query with a filter on rfid.
        if rfid is not None:
            qry_latest_id = qry_latest_id.filter(ChargeSessionModel.rfid == str(rfid))
        #  Now query the ChargeSession that we're interested in (latest for device or latest for device AND rfid).
        latest_charge_session = None
        try:
            latest_charge_session = db_session.query(ChargeSessionModel) \
                                              .filter(ChargeSessionModel.id == qry_latest_id) \
                                              .first()
        except Exception as e:
            # Nothing to roll back
            self.logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
        return latest_charge_session


    @staticmethod
    def get_open_charge_session_for_device(device) -> ChargeSessionModel:
        db_session = DbSession()

        open_charge_session_for_device = None
        try:
            # Build query to get id of latest chargesession for this device.
            open_charge_session_for_device = db_session.query(ChargeSessionModel) \
                            .filter(ChargeSessionModel.energy_device_id == device) \
                            .filter(ChargeSessionModel.end_time == None) \
                            .order_by(ChargeSessionModel.start_time.desc()) \
                            .first()    # Call first to return an object instead of an array
        except Exception as e:
            # Nothing to roll back
            self.logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
        return open_charge_session_for_device


    def __repr(self) -> str:
        return '<id {}>'.format(self.id)


    def get_last_n_sessions_since(self, energy_device_id=None, since_ts=None, n=-1) -> typing.List[ChargeSessionModel]:
        db_session = DbSession()
        csm = None
        try:
            if (n == -1):
                if (since_ts == None):
                    if (energy_device_id == None):
                        csm = db_session.query(ChargeSessionModel) \
                                        .order_by(ChargeSessionModel.start_time.desc()) \
                                        .all()
                    else:  # filter energy_device_id
                        csm = db_session.query(ChargeSessionModel) \
                                        .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                        .order_by(ChargeSessionModel.start_time.desc()) \
                                        .all()
                else:  # filter since_ts
                    if (energy_device_id == None):
                        csm = db_session.query(ChargeSessionModel) \
                                        .filter(ChargeSessionModel.start_time >= self.date_str_to_datetime(since_ts)) \
                                        .order_by(ChargeSessionModel.start_time.desc()) \
                                        .all()
                    else:  # filter energy_device_id
                        csm = db_session.query(ChargeSessionModel) \
                                        .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                        .filter(ChargeSessionModel.start_time >= self.date_str_to_datetime(since_ts)) \
                                        .order_by(ChargeSessionModel.start_time.desc()) \
                                        .all()
            else:  # limit n
                if (since_ts == None):
                    if (energy_device_id == None):
                        csm = db_session.query(ChargeSessionModel) \
                                        .order_by(ChargeSessionModel.start_time.desc()) \
                                        .limit(n) \
                                        .all()
                    else:  # filter energy_device_id
                        csm = db_session.query(ChargeSessionModel) \
                                        .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                        .order_by(ChargeSessionModel.start_time.desc()) \
                                        .limit(n) \
                                        .all()
                else:  # filter since_ts
                    if (energy_device_id == None):
                        csm = db_session.query(ChargeSessionModel) \
                                        .filter(ChargeSessionModel.start_time >= self.date_str_to_datetime(since_ts)) \
                                        .order_by(ChargeSessionModel.start_time.desc()) \
                                        .limit(n) \
                                        .all()
                    else:  # filter energy_device_id
                        csm = db_session.query(ChargeSessionModel) \
                                        .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                        .filter(ChargeSessionModel.start_time >= self.date_str_to_datetime(since_ts)) \
                                        .order_by(ChargeSessionModel.start_time.desc()) \
                                        .limit(n) \
                                        .all()
        except Exception as e:
            # Nothing to roll back
            self.logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
        return csm


    def date_str_to_datetime(self, date_time_str: str) -> datetime:
        return datetime.strptime(date_time_str, '%d/%m/%Y, %H:%M:%S')


    # convert into JSON:
    def to_json(self) -> str:
        return (
            json.dumps({
                "id": str(self.id),
                "energy_device_id": str(self.energy_device_id),
                "start_time": (
                    str(self.start_time.strftime("%d/%m/%Y, %H:%M:%S")) if self.start_time is not None else None
                    ),
                "rfid": self.rfid,
                "start_value": str(self.start_value),
                "end_value": str(self.end_value),
                "tariff": str(self.tariff),
                "total_energy": str(self.total_energy),
                "total_price": str(self.total_price),
                "km": str(self.km),
                "end_time": (
                    str(self.end_time.strftime("%d/%m/%Y, %H:%M:%S")) if self.end_time is not None else None
                    ),
                "trigger": str(self.trigger)
            })
        )


    # convert into JSON:
    def to_str(self) -> str:
        return ({
                "id": str(self.id),
                "energy_device_id": str(self.energy_device_id),
                "start_time": (
                    str(self.start_time.strftime("%d/%m/%Y, %H:%M:%S")) if self.start_time is not None else None
                    ),
                "rfid": self.rfid,
                "start_value": str(self.start_value),
                "end_value": str(self.end_value),
                "tariff": str(self.tariff),
                "total_energy": str(self.total_energy),
                "total_price": str(self.total_price),
                "km": str(self.km),
                "end_time": (
                    str(self.end_time.strftime("%d/%m/%Y, %H:%M:%S")) if self.end_time is not None else None
                    ),
                "trigger": str(self.trigger)
            })


    # convert into dict:
    def to_dict(self) -> typing.TypedDict:
        return ({
            "id": str(self.id),
            "energy_device_id": str(self.energy_device_id),
            "start_time": (
                str(self.start_time.strftime("%d/%m/%Y, %H:%M:%S")) if self.start_time is not None else None
                ),
            "rfid": self.rfid,
            "start_value": str(self.start_value),
            "end_value": str(self.end_value),
            "tariff": str(self.tariff),
            "total_energy": str(self.total_energy),
            "total_price": str(self.total_price),
            "km": str(self.km),
            "end_time": (
                str(self.end_time.strftime("%d/%m/%Y, %H:%M:%S")) if self.end_time is not None else None
                ),
            "trigger": str(self.trigger)
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
    trigger = fields.Str(required=True)

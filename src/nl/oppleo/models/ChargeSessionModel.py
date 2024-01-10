# Return type hints https://docs.python.org/3/library/typing.html
from __future__ import annotations
import typing

from marshmallow import fields, Schema
from datetime import datetime
import logging

from sqlalchemy import orm, func, Column, Integer, String, Float, DateTime, desc, update
from sqlalchemy.exc import InvalidRequestError

from nl.oppleo.models.Base import Base, DbSession
from nl.oppleo.exceptions.Exceptions import DbException
import json

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig

oppleoSystemConfig = OppleoSystemConfig()

class ChargeSessionModel(Base):
    """
    Charge Session Model
    """

    __logger = None

    # table name
    __tablename__ = 'charge_session'  # -> sessions
    fieldList = ['rfid', 'energy_device_id', 'start_value', 'end_value', 'start_time', 'end_time', 'tariff', 'total_energy', 'total_price', 'km', 'trigger']
   
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
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(__name__))    


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
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            db_session.rollback()
            self.__logger.error("Could not save to {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not save to {} table in database".format(self.__tablename__ ))


    def update(self, data) -> None:
        for key, item in data.items():
            setattr(self, key, item)
        self.modified_at = datetime.now()
        db_session = DbSession()
        try:
            db_session.add(self)
            db_session.commit()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            db_session.rollback()
            self.__logger.error("Could not update to {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not update to {} table in database".format(self.__tablename__ ))


    def delete(self) -> None:
        db_session = DbSession()
        try:
            db_session.delete(self)
            db_session.commit()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            db_session.rollback()
            self.__logger.error("Could not delete from {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not delete from {} table in database".format(self.__tablename__ ))


    @staticmethod
    def get_all_sessions() -> typing.List[ChargeSessionModel] | None:
        db_session = DbSession()
        csm = None
        try:
            csm = db_session.query(ChargeSessionModel) \
                            .all()
        except InvalidRequestError as e:
            ChargeSessionModel.__cleanupDbSession(db_session, ChargeSessionModel.__class__)
        except Exception as e:
            # Nothing to roll back
            ChargeSessionModel.__logger.error("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ))
        return csm


    @staticmethod
    def get_one_charge_session(id) -> ChargeSessionModel | None:
        db_session = DbSession()
        csm = None

        try:
            csm = db_session.query(ChargeSessionModel) \
                            .filter(ChargeSessionModel.id == id) \
                            .limit(1) \
                            .all()
        except InvalidRequestError as e:
            ChargeSessionModel.__cleanupDbSession(db_session, ChargeSessionModel.__class__)
        except Exception as e:
            # Nothing to roll back
            ChargeSessionModel.__logger.error("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ))

        return None if len(csm) < 1 else csm[0]
       

    """
    Returns session with specific values, used for condensing charge sessions
    """
    @staticmethod
    def get_specific_closed_charge_session(energy_device_id, rfid, km, end_value, tariff) -> ChargeSessionModel | None:
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
                            .order_by(desc(ChargeSessionModel.id)) \
                            .first()
        except InvalidRequestError as e:
            ChargeSessionModel.__cleanupDbSession(db_session, ChargeSessionModel.__class__)
        except:
            # Nothing to roll back
            ChargeSessionModel.__logger.error("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ))
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
    def get_latest_charge_session(device, rfid=None) -> ChargeSessionModel | None:
        db_session = DbSession()
        # Build query to get id of latest chargesession for this device.
        qry_latest_id = db_session.query(func.max(ChargeSessionModel.id)) \
                                  .filter(ChargeSessionModel.energy_device_id == device)
        # If rfid is specified, expand the query with a filter on rfid.
        if rfid is not None:
            qry_latest_id = qry_latest_id.filter(ChargeSessionModel.rfid == str(rfid))
        #  Now query the ChargeSession that we're interested in (latest for device or latest for device AND rfid).
        latest_charge_session = None
        try:
            latest_charge_session = db_session.query(ChargeSessionModel) \
                                              .filter(ChargeSessionModel.id == qry_latest_id) \
                                              .first()
        except InvalidRequestError as e:
            ChargeSessionModel.__cleanupDbSession(db_session, ChargeSessionModel.__class__)
        except Exception as e:
            # Nothing to roll back
            ChargeSessionModel.__logger.error("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ))
        return latest_charge_session


    @staticmethod
    def migrateEnergyDevice(fromEnergyDeviceId=None, toEnergyDeviceId=None) -> ChargeSessionModel | None:
        db_session = DbSession()
        try:

            sessionList = db_session.query(ChargeSessionModel).filter(ChargeSessionModel.energy_device_id == fromEnergyDeviceId)
            for chargeSession in sessionList:
                chargeSession.energy_device_id = toEnergyDeviceId
                #chargeSession.save()
            db_session.commit()

        except InvalidRequestError as e:
            ChargeSessionModel.__cleanupDbSession(db_session, ChargeSessionModel.__class__)
        except Exception as e:
            # Nothing to roll back
            ChargeSessionModel.__logger.error("Could not migrate sessions from {} to {} in table {} in database. ({})".format(
                    fromEnergyDeviceId, toEnergyDeviceId, ChargeSessionModel.__tablename__, str(e) 
                ), exc_info=True)
            
            raise DbException("Could not migrate sessions from {} to {} in table {} in database. ({})".format(
                    fromEnergyDeviceId, toEnergyDeviceId, ChargeSessionModel.__tablename__, str(e) 
                ))
        return

    @staticmethod
    def getOpenChargeSession(device=None) -> ChargeSessionModel | None:
        db_session = DbSession()

        if device is None:
            return None

        #  Now query the ChargeSession that we're interested in (latest for device).
        try:
            latest = db_session.query(ChargeSessionModel)   \
                        .filter(ChargeSessionModel.energy_device_id == device)    \
                        .order_by(ChargeSessionModel.id.desc()) \
                        .first()

        except InvalidRequestError as e:
            ChargeSessionModel.__logger.error("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ), exc_info=True)
            ChargeSessionModel.__cleanupDbSession(db_session, ChargeSessionModel.__class__)
            return None
        except Exception as e:
            # Nothing to roll back
            ChargeSessionModel.__logger.error("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ))

        if (latest is None or latest.end_time != None):
            # No recent open charge session
            return None

        return latest


    @staticmethod
    def get_open_charge_session_for_device(device) -> ChargeSessionModel | None:
        db_session = DbSession()

        open_charge_session_for_device = None
        try:
            # Build query to get id of latest chargesession for this device.
            open_charge_session_for_device = db_session.query(ChargeSessionModel) \
                            .filter(ChargeSessionModel.energy_device_id == device) \
                            .filter(ChargeSessionModel.end_time == None) \
                            .order_by(desc(ChargeSessionModel.start_time)) \
                            .first()    # Call first to return an object instead of an array
        except InvalidRequestError as e:
            ChargeSessionModel.__cleanupDbSession(db_session, ChargeSessionModel.__class__)
            ChargeSessionModel.__logger.error("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ), exc_info=True)
        except Exception as e:
            # Nothing to roll back
            ChargeSessionModel.__logger.error("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ))
        return open_charge_session_for_device

    @staticmethod
    def has_open_charge_session_for_device(device) -> bool:
        db_session = DbSession()

        open_charge_session_for_device = None
        try:
            # Build query to get id of latest chargesession for this device.
            open_charge_session_for_device = db_session.query(ChargeSessionModel) \
                            .filter(ChargeSessionModel.energy_device_id == device) \
                            .filter(ChargeSessionModel.end_time == None) \
                            .order_by(desc(ChargeSessionModel.start_time)) \
                            .first()    # Call first to return an object instead of an array
        except InvalidRequestError as e:
            ChargeSessionModel.__cleanupDbSession(db_session, ChargeSessionModel.__class__)
        except Exception as e:
            # Nothing to roll back
            ChargeSessionModel.__logger.error("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ))
        return open_charge_session_for_device != None

    @staticmethod
    def get_charge_session_count_for_rfid(rfid) -> int:
        db_session = DbSession()

        charge_session_count = 0
        try:
            # Build query to get id of latest chargesession for this device.
            charge_session_count = db_session.query(ChargeSessionModel) \
                            .filter(ChargeSessionModel.rfid == rfid) \
                            .count()    # Count the number of sessions
        except InvalidRequestError as e:
            ChargeSessionModel.__cleanupDbSession(db_session, ChargeSessionModel.__class__)
        except Exception as e:
            # Nothing to roll back
            ChargeSessionModel.__logger.error("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ))
        return charge_session_count

    def __repr(self) -> str:
        return '<id {}>'.format(self.id)


    """
        Filtered by end time
        from_ts and to_ts are date string ('%d/%m/%Y, %H:%M:%S')
        Date values as zero-padded decimal number (01, 02, ...) and month 1-based (Jan = 1)
    """
    def get_max_n_sessions_between(self, energy_device_id=None, from_ts=None, to_ts=None, n=-1) -> typing.List[ChargeSessionModel] | None:
        db_session = DbSession()
        csm = None
        try:
            if (n == -1):               # No limit
                if (from_ts == None):   # No from timestamp
                    if (to_ts == None): # No to timestamp
                        if (energy_device_id == None):   # All devices
                            csm = db_session.query(ChargeSessionModel) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .all()
                        else:           # filter energy_device_id
                            csm = db_session.query(ChargeSessionModel) \
                                            .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .all()
                    else:               # filter to timestamp
                        if (energy_device_id == None):   # All devices
                            csm = db_session.query(ChargeSessionModel) \
                                            .filter(ChargeSessionModel.end_time < self.date_str_to_datetime(to_ts)) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .all()
                        else:           # filter energy_device_id
                            csm = db_session.query(ChargeSessionModel) \
                                            .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                            .filter(ChargeSessionModel.end_time < self.date_str_to_datetime(to_ts)) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .all()
                else:                   # filter from timestamp
                    if (to_ts == None): # No to timestamp
                        if (energy_device_id == None):      # All devices
                            csm = db_session.query(ChargeSessionModel) \
                                            .filter(ChargeSessionModel.end_time >= self.date_str_to_datetime(from_ts)) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .all()
                        else:               # filter energy_device_id
                            csm = db_session.query(ChargeSessionModel) \
                                            .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                            .filter(ChargeSessionModel.end_time >= self.date_str_to_datetime(from_ts)) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .all()
                    else:                   # filter to timestamp
                        if (energy_device_id == None):      # All devices
                            csm = db_session.query(ChargeSessionModel) \
                                            .filter(ChargeSessionModel.end_time >= self.date_str_to_datetime(from_ts)) \
                                            .filter(ChargeSessionModel.end_time < self.date_str_to_datetime(to_ts)) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .all()
                        else:               # filter energy_device_id
                            csm = db_session.query(ChargeSessionModel) \
                                            .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                            .filter(ChargeSessionModel.end_time >= self.date_str_to_datetime(from_ts)) \
                                            .filter(ChargeSessionModel.end_time < self.date_str_to_datetime(to_ts)) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .all()

            else:  # limit n
                if (from_ts == None):   # No from timestamp
                    if (to_ts == None): # No to timestamp
                        if (energy_device_id == None):   # All devices
                            csm = db_session.query(ChargeSessionModel) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .limit(n) \
                                            .all()
                        else:           # filter energy_device_id
                            csm = db_session.query(ChargeSessionModel) \
                                            .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .limit(n) \
                                            .all()
                    else:               # filter to timestamp
                        if (energy_device_id == None):   # All devices
                            csm = db_session.query(ChargeSessionModel) \
                                            .filter(ChargeSessionModel.end_time < self.date_str_to_datetime(to_ts)) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .limit(n) \
                                            .all()
                        else:           # filter energy_device_id
                            csm = db_session.query(ChargeSessionModel) \
                                            .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                            .filter(ChargeSessionModel.end_time < self.date_str_to_datetime(to_ts)) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .limit(n) \
                                            .all()
                else:                   # filter from timestamp
                    if (to_ts == None): # No to timestamp
                        if (energy_device_id == None):      # All devices
                            csm = db_session.query(ChargeSessionModel) \
                                            .filter(ChargeSessionModel.end_time >= self.date_str_to_datetime(from_ts)) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .limit(n) \
                                            .all()
                        else:               # filter energy_device_id
                            csm = db_session.query(ChargeSessionModel) \
                                            .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                            .filter(ChargeSessionModel.end_time >= self.date_str_to_datetime(from_ts)) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .limit(n) \
                                            .all()
                    else:                   # filter to timestamp
                        if (energy_device_id == None):      # All devices
                            csm = db_session.query(ChargeSessionModel) \
                                            .filter(ChargeSessionModel.end_time >= self.date_str_to_datetime(from_ts)) \
                                            .filter(ChargeSessionModel.end_time < self.date_str_to_datetime(to_ts)) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .limit(n) \
                                            .all()
                        else:               # filter energy_device_id
                            csm = db_session.query(ChargeSessionModel) \
                                            .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                            .filter(ChargeSessionModel.end_time >= self.date_str_to_datetime(from_ts)) \
                                            .filter(ChargeSessionModel.end_time < self.date_str_to_datetime(to_ts)) \
                                            .order_by(desc(ChargeSessionModel.start_time)) \
                                            .limit(n) \
                                            .all()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            # Nothing to roll back
            self.__logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(self.__tablename__ ))
        return csm

    """
        since_ts date string ('%d/%m/%Y, %H:%M:%S')
        Date values as zero-padded decimal number (01, 02, ...) and month 1-based (Jan = 1)
    """
    def get_last_n_sessions_since(self, energy_device_id=None, since_ts=None, n=-1) -> typing.List[ChargeSessionModel] | None:
        db_session = DbSession()
        csm = None
        try:
            if (n == -1):
                if (since_ts == None):
                    if (energy_device_id == None):
                        csm = db_session.query(ChargeSessionModel) \
                                        .order_by(desc(ChargeSessionModel.start_time)) \
                                        .all()
                    else:  # filter energy_device_id
                        csm = db_session.query(ChargeSessionModel) \
                                        .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                        .order_by(desc(ChargeSessionModel.start_time)) \
                                        .all()
                else:  # filter since_ts
                    if (energy_device_id == None):
                        csm = db_session.query(ChargeSessionModel) \
                                        .filter(ChargeSessionModel.start_time >= self.date_str_to_datetime(since_ts)) \
                                        .order_by(desc(ChargeSessionModel.start_time)) \
                                        .all()
                    else:  # filter energy_device_id
                        csm = db_session.query(ChargeSessionModel) \
                                        .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                        .filter(ChargeSessionModel.start_time >= self.date_str_to_datetime(since_ts)) \
                                        .order_by(desc(ChargeSessionModel.start_time)) \
                                        .all()
            else:  # limit n
                if (since_ts == None):
                    if (energy_device_id == None):
                        csm = db_session.query(ChargeSessionModel) \
                                        .order_by(desc(ChargeSessionModel.start_time)) \
                                        .limit(n) \
                                        .all()
                    else:  # filter energy_device_id
                        csm = db_session.query(ChargeSessionModel) \
                                        .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                        .order_by(desc(ChargeSessionModel.start_time)) \
                                        .limit(n) \
                                        .all()
                else:  # filter since_ts
                    if (energy_device_id == None):
                        csm = db_session.query(ChargeSessionModel) \
                                        .filter(ChargeSessionModel.start_time >= self.date_str_to_datetime(since_ts)) \
                                        .order_by(desc(ChargeSessionModel.start_time)) \
                                        .limit(n) \
                                        .all()
                    else:  # filter energy_device_id
                        csm = db_session.query(ChargeSessionModel) \
                                        .filter(ChargeSessionModel.energy_device_id == energy_device_id) \
                                        .filter(ChargeSessionModel.start_time >= self.date_str_to_datetime(since_ts)) \
                                        .order_by(desc(ChargeSessionModel.start_time)) \
                                        .limit(n) \
                                        .all()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            # Nothing to roll back
            self.__logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(self.__tablename__ ))
        return csm

    """
        %d  Day of the month as a zero-padded decimal. 01, 02, ..., 31
        %m	Month as a zero-padded decimal number.	01, 02, ..., 12
        %Y	Year with century as a decimal number.	2013, 2019 etc.
        %H	Hour (24-hour clock) as a zero-padded decimal number.	00, 01, ..., 23
        %M	Minute as a zero-padded decimal number.	00, 01, ..., 59
        %S	Second as a zero-padded decimal number.	00, 01, ..., 59
    """
    def date_str_to_datetime(self, date_time_str: str) -> datetime:
        return datetime.strptime(date_time_str, '%d/%m/%Y, %H:%M:%S')

    def datetime_to_date_str(self, date_time:datetime=None) -> str:
        return str(date_time.strftime("%d/%m/%Y, %H:%M:%S")) if date_time is not None else None

    """
        Overview total energy and price amounts per month
            SELECT DATE_PART('year', end_time) AS Year, DATE_PART('month', end_time) AS Month, SUM(total_energy) AS TotalEnergy, SUM(total_price) AS Price FROM charge_session GROUP BY DATE_PART('year', end_time), DATE_PART('month', end_time) ORDER BY Year DESC, Month ASC;

            SELECT DATE_PART('year', end_time) AS Year, DATE_PART('month', end_time) AS Month, SUM(total_energy) AS TotalEnergy, SUM(total_price) AS Price
            FROM charge_session
            GROUP BY DATE_PART('year', end_time), DATE_PART('month', end_time)
            ORDER BY Month ASC

            select distinct date_part('year', date_created) from charge_session;
            result = session.query(distinct(func.date_part('YEAR', 'date_created')))

            - extract vs date_part, extract seems to be the SQL standard
            SELECT DATE_PART('year', end_time) AS Year, 
            SELECT EXTRACT(year FROM end_time) AS Year FROM charge_session
            
            SELECT EXTRACT(year FROM end_time) AS Year, EXTRACT(month FROM end_time) AS Month, SUM(total_energy) AS TotalEnergy, SUM(total_price) AS Price FROM charge_session GROUP BY EXTRACT(year FROM end_time), EXTRACT(month FROM end_time) ORDER BY Year DESC, Month ASC;

            SELECT EXTRACT(year FROM end_time) AS Year, EXTRACT(month FROM end_time) AS Month, SUM(total_energy) AS TotalEnergy, SUM(total_price) AS Price 
            FROM charge_session 
            GROUP BY EXTRACT(year FROM end_time), EXTRACT(month FROM end_time) 
            ORDER BY Year DESC, Month ASC;

            select distinct EXTRACT(year, date_created) from date_created;
            result = session.query(distinct(func.extract('YEAR', 'date_created')))

    """
    @staticmethod
    def get_history(energy_device_id=None) -> typing.List[ChargeSessionModel] | None:
        db_session = DbSession()

        from sqlalchemy import func, extract #, distinct

        csm = None
        try:
            if (energy_device_id == None):
                csm = db_session.query( func.sum(ChargeSessionModel.total_energy).label('TotalEnergy'), \
                                        func.sum(ChargeSessionModel.total_price).label('TotalPrice'),   \
                                        extract('year', ChargeSessionModel.end_time).label('Year'),     \
                                        extract('month', ChargeSessionModel.end_time).label('Month'))   \
                                        .group_by( extract('year', ChargeSessionModel.end_time),        \
                                                extract('month', ChargeSessionModel.end_time))          \
                                        .all()
            else:  # filter energy_device_id
                csm = db_session.query( func.sum(ChargeSessionModel.total_energy).label('TotalEnergy'),     \
                                        func.sum(ChargeSessionModel.total_price).label('TotalPrice'),       \
                                        extract('year', ChargeSessionModel.end_time).label('Year'),         \
                                        extract('month', ChargeSessionModel.end_time).label('Month'))       \
                                        .filter(ChargeSessionModel.energy_device_id == energy_device_id)    \
                                        .group_by( extract('year', ChargeSessionModel.end_time),            \
                                                extract('month', ChargeSessionModel.end_time))              \
                                        .all()

        except InvalidRequestError as e:
            ChargeSessionModel.__cleanupDbSession(db_session, ChargeSessionModel.__class__)
        except Exception as e:
            # Nothing to roll back
            ChargeSessionModel.__logger.error("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(ChargeSessionModel.__tablename__ ))
        return csm


    # convert into JSON:
    def to_json(self) -> str:
        return (
            json.dumps({
                "id": str(self.id),
                "energy_device_id": str(self.energy_device_id),
                "start_time": self.datetime_to_date_str( self.start_time ),
                "rfid": self.rfid,
                "start_value": str(self.start_value),
                "end_value": str(self.end_value),
                "tariff": str(self.tariff),
                "total_energy": str(self.total_energy),
                "total_price": str(self.total_price),
                "km": str(self.km),
                "end_time": self.datetime_to_date_str( self.end_time ),
                "trigger": str(self.trigger)
            },
            default=str
            )
        )


    # convert into JSON:
    def to_str(self) -> dict:
        return ({
                "id": str(self.id),
                "energy_device_id": str(self.energy_device_id),
                "start_time": self.datetime_to_date_str( self.start_time ),
                "rfid": self.rfid,
                "start_value": str(self.start_value),
                "end_value": str(self.end_value),
                "tariff": str(self.tariff),
                "total_energy": str(self.total_energy),
                "total_price": str(self.total_price),
                "km": str(self.km),
                "end_time": self.datetime_to_date_str( self.end_time ),
                "trigger": str(self.trigger)
            })


    # convert into dict:
    def to_dict(self) -> dict:
        return ({
            "id": str(self.id),
            "energy_device_id": str(self.energy_device_id),
            "start_time": self.datetime_to_date_str( self.start_time ),
            "rfid": self.rfid,
            "start_value": str(self.start_value),
            "end_value": str(self.end_value),
            "tariff": str(self.tariff),
            "total_energy": str(self.total_energy),
            "total_price": str(self.total_price),
            "km": str(self.km),
            "end_time": self.datetime_to_date_str( self.end_time ),
            "trigger": str(self.trigger)
        })

    """
        Try to fix any database errors including
            - sqlalchemy.exc.InvalidRequestError: Can't reconnect until invalid transaction is rolled back
    """
    @staticmethod
    def __cleanupDbSession(db_session=None, cn=None):
        logger = logging.getLogger('nl.oppleo.models.ChargeSessionModel')
        logger.debug(".__cleanupDbSession() - Trying to cleanup database session, called from {}".format(cn))
        try:
            db_session.remove()
            if db_session.is_active:
                db_session.rollback()
        except Exception as e:
            logger.debug(".__cleanupDbSession() - Exception trying to cleanup database session from {}".format(cn), exc_info=True)


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

import datetime
import logging

from marshmallow import fields, Schema
from marshmallow.fields import Boolean, Integer

from sqlalchemy import orm, Column, String, Float, DateTime, Integer, Boolean, Time, desc
from sqlalchemy.exc import InvalidRequestError
"""
When saving an object in another Thread, the attached Session (DbSession) can be from the previous Thread. This causes issues.
Call make_transient_to_detached to detach the object. Changes cannot be flushed automatically, but DbSession.add() will add it 
to a valid session again. because the primary key of this object remains, this can be done with no issues here.
    sqlalchemy.orm.make_transient(instance)
    sqlalchemy.orm.make_transient_to_detached(instance)
https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.make_transient_to_detached
"""
from sqlalchemy.orm import make_transient, make_transient_to_detached


from nl.oppleo.models.Base import Base, DbSession
from nl.oppleo.exceptions.Exceptions import DbException

""" 
    The charger config model refers to a single charger config, represented by a single database row.
"""

class ChargerConfigModel(Base):
    logger = logging.getLogger('nl.oppleo.models.ChargerConfigModel')
    __tablename__ = 'charger_config'

    charger_name = Column(String(100), primary_key=True)
    charger_tariff = Column(Float)        # €/kWh
    modified_at = Column(DateTime)        # Last config update

    secret_key = Column(String(100))
    wtf_csrf_secret_key = Column(String(100))

    use_reloader = Column(Boolean) 

    factor_whkm = Column(Integer) 
    modbus_interval = Column(Integer)

    autosession_enabled = Column(Boolean) 
    autosession_minutes = Column(Integer) 
    autosession_energy = Column(Float) 
    autosession_condense_same_odometer = Column(Boolean) 

    pulseled_min = Column(Integer) 
    pulseled_max = Column(Integer) 
    gpio_mode = Column(String(10)) 
    pin_led_red = Column(Integer) 
    pin_led_green = Column(Integer) 
    pin_led_blue = Column(Integer) 
    pin_buzzer = Column(Integer) 
    pin_evse_switch = Column(Integer) 
    pin_evse_led = Column(Integer) 

    peakhours_offpeak_enabled = Column(Boolean)
    peakhours_allow_peak_one_period = Column(Boolean) 

    webcharge_on_dashboard = Column(Boolean) 
    auth_webcharge = Column(Boolean) 

    restrict_dashboard_access = Column(Boolean) 
    restrict_menu = Column(Boolean) 

    allow_local_dashboard_access = Column(Boolean) 
    router_ip_address = Column(String(20)) 

    receipt_prefix = Column(String(20))

    backup_enabled = Column(Boolean)
    backup_interval = Column(String(1))
    backup_interval_weekday = Column(String(200))
    backup_interval_calday = Column(String(300))
    backup_time_of_day = Column(Time)
    backup_local_history = Column(Integer)
    backup_success_timestamp = Column(DateTime)  

    os_backup_enabled = Column(Boolean)
    os_backup_type = Column(String(20))
    os_backup_history = Column(Integer)

    smb_backup_servername_or_ip_address = Column(String(20))
    smb_backup_username = Column(String(60))
    smb_backup_password = Column(String(100))
    smb_backup_service_name  = Column(String(200))
    smb_backup_remote_path = Column(String(256))


    def __init__(self):
        self.logger.debug('.init()')

    # sqlalchemy calls __new__ not __init__ on reconstructing from database. Decorator to call this method
    @orm.reconstructor   
    def init_on_load(self):
        self.logger.debug('.init_on_load()')
        self.__init__()

    def set(self, data:dict):
        self.logger.debug('.set()')
        for key in data:
            self.logger.debug('.set() key:{} value:{}'.format(key, data.get(key)))
            setattr(self, key, data.get(key))
        self.modified_at = datetime.datetime.now()
        self.logger.debug('.set() modified_at:{}'.format(self.modified_at))

    """
        Set a single variable
    """
    def setAndSave(self, key, value, allowed=None):
        self.logger.debug('.setAndSave() key:{} value:{} range:{}'.format(key, value, allowed))
        curVal = getattr(self, key)
        self.logger.debug('.setAndSave() curVal:{}'.format(curVal))
        if not isinstance(value, type(curVal)):
            self.logger.debug(".setAndSave() {} TypeError: {} must be type {}".format(key, type(curVal)))
            raise TypeError("{} must be type {}".format(key, type(curVal)))
        self.logger.debug('.setAndSave() no TypeError')
        if allowed is not None and value not in allowed:
            self.logger.debug(".setAndSave() {} ValueError: value {} of key {} not within range {}".format(value, key, allowed))
            raise ValueError("{} value {} of key {} not within range {}".format(value, key, allowed))
        self.logger.debug('.setAndSave() no ValueError')
        setattr(self, key, value)
        self.logger.debug('.setAndSave() curVal:{} getattr(self, key)={}'.format(curVal, getattr(self, key)))
        if curVal != getattr(self, key):
            # Value changed
            self.modified_at = datetime.datetime.now()
            self.save()

    def save(self):
        self.logger.debug(".save()")
        db_session = DbSession()
        # Prevent expiration after the session is closed or object is made transient or disconnected
        db_session.expire_on_commit = False
        try:
            # No need to 'add', committing this class
            db_session.add(self)
            db_session.commit()
            # Keep it detached
            make_transient(self)
            make_transient_to_detached(self)
        except InvalidRequestError as e:
            self.logger.error(".save() - Could not commit to {} table in database".format(self.__tablename__ ), exc_info=True)
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            db_session.rollback()
            self.logger.error(".save() - Could not commit to {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not commit to {} table in database".format(self.__tablename__ ))


    def delete(self):
        db_session = DbSession()
        db_session.expire_on_commit = True
        try:
            db_session.delete(self)
            db_session.commit()
            # Keep it detached
            make_transient(self)
            make_transient_to_detached(self)
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            db_session.rollback()
            self.logger.error("Could not delete from {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not delete from {} table in database".format(self.__tablename__ ))


    @staticmethod
    def get_config():
        db_session = DbSession()
        # Prevent expiration after the session is closed or object is made transient or disconnected
        db_session.expire_on_commit = False
        ccm = None
        try:
            # Should be only one, return last modified
            ccm = db_session.query(ChargerConfigModel) \
                            .order_by(desc(ChargerConfigModel.modified_at)) \
                            .first()
            # Detach (not transient) from database, allows saving in other Threads
            # https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.make_transient_to_detached
            make_transient(ccm)
            make_transient_to_detached(ccm)
        except InvalidRequestError as e:
            ChargerConfigModel.__cleanupDbSession(db_session, ChargerConfigModel.__class__)
        except Exception as e:
            # Nothing to roll back
            ChargerConfigModel.logger.error("Could not query from {} table in database".format(ChargerConfigModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(ChargerConfigModel.__tablename__ ))
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

    """
        Try to fix any database errors including
            - sqlalchemy.exc.InvalidRequestError: Can't reconnect until invalid transaction is rolled back
    """
    @staticmethod
    def __cleanupDbSession(db_session=None, cn=None):
        logger = logging.getLogger('nl.oppleo.models.ChargerConfigModel')
        logger.debug(".__cleanupDbSession() - Trying to cleanup database session, called from {}".format(cn))
        try:
            db_session.remove()
            if db_session.is_active:
                db_session.rollback()
        except Exception as e:
            logger.debug(".__cleanupDbSession() - Exception trying to cleanup database session from {}".format(cn), exc_info=True)



class ChargerConfigSchema(Schema):
    """
    ChargerConfigModel Schema
    """
    charger_name = fields.Str(required=True)
    charger_tariff = fields.Float(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)

    secret_key = fields.Str(dump_only=True)
    wtf_csrf_secret_key = fields.Str(dump_only=True)

    use_reloader = fields.Bool(dump_only=True)

    factor_whkm = fields.Float(dump_only=True)
    modbus_interval = fields.Integer(dump_only=True)

    autosession_enabled = fields.Bool(dump_only=True)
    autosession_minutes = fields.Int(dump_only=True)
    autosession_energy = fields.Float(dump_only=True)
    autosession_condense_same_odometer = fields.Bool(dump_only=True)


    pulseled_min = fields.Int(dump_only=True)
    pulseled_max = fields.Int(dump_only=True)
    gpio_mode = fields.Str(dump_only=True)
    pin_led_red = fields.Int(dump_only=True)
    pin_led_green = fields.Int(dump_only=True)
    pin_led_blue = fields.Int(dump_only=True)
    pin_buzzer = fields.Int(dump_only=True)

    pin_evse_switch = fields.Int(dump_only=True)
    pin_evse_led = fields.Int(dump_only=True)

    peakhours_offpeak_enabled = fields.Bool(dump_only=True)
    peakhours_allow_peak_one_period = fields.Bool(dump_only=True)

    webcharge_on_dashboard = fields.Bool(dump_only=True)
    auth_webcharge = fields.Bool(dump_only=True)

    restrict_dashboard_access = fields.Bool(dump_only=True)
    restrict_menu = fields.Bool(dump_only=True)

    allow_local_dashboard_access = fields.Bool(dump_only=True)
    router_ip_address = fields.Str(dump_only=True)

    receipt_prefix = fields.Str(dump_only=True)

    backup_enabled = fields.Bool(dump_only=True)
    backup_interval = fields.Str(dump_only=True)
    backup_interval_weekday = fields.Str(dump_only=True)
    backup_interval_calday = fields.Str(dump_only=True)
    backup_time_of_day = fields.Time(dump_only=True)
    backup_local_history = fields.Int(dump_only=True)
    backup_success_timestamp = fields.DateTime(dump_only=True)

    os_backup_enabled = fields.Bool(dump_only=True)
    os_backup_type = fields.Str(dump_only=True)
    os_backup_history = fields.Int(dump_only=True)

    smb_backup_servername_or_ip_address = fields.Str(dump_only=True)
    smb_backup_username = fields.Str(dump_only=True)
    smb_backup_password = fields.Str(dump_only=True)
    smb_backup_service_name  = fields.Str(dump_only=True)
    smb_backup_remote_path = fields.Str(dump_only=True)

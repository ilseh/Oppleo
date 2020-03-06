import datetime
import logging

from marshmallow import fields, Schema
from marshmallow.fields import Boolean, Integer

from sqlalchemy import orm, Column, String, Float, DateTime, Integer, Boolean
from nl.oppleo.models.Base import Base, DbSession


class ChargerConfigModel(Base):
    logger = logging.getLogger('nl.oppleo.models.ChargerConfigModel')
    __tablename__ = 'charger_config'

    charger_name = Column(String(100), primary_key=True)
    charger_tariff = Column(Float)        # €/kWh
    modified_at = Column(DateTime)        # Last config update

    secret_key = Column(String(100))
    wtf_csrf_secret_key = Column(String(100))

    http_host = Column(String(64))
    http_port = Column(Integer) 
    use_reloader = Column(Boolean) 

    factor_whkm = Column(Integer) 

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

    peakhours_offpeak_enabled = Column(Boolean)
    peakhours_allow_peak_one_period = Column(Boolean) 

    prowl_enabled = Column(Boolean) 
    prowl_apikey = Column(String(100)) 


    def __init__(self):
        pass


    # sqlalchemy calls __new__ not __init__ on reconstructing from database. Decorator to call this method
    @orm.reconstructor   
    def init_on_load(self):
        self.__init__()

    def set(self, data):
        for key in data:
            setattr(self, key, data.get(key))
        self.modified_at = datetime.datetime.now()

    def save(self):
        db_session = DbSession()
        try:
            db_session.add(self)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            self.logger.error("Could not commit to {} table in database".format(self.__tablename__ ), exc_info=True)


    def delete(self):
        db_session = DbSession()
        try:
            db_session.delete(self)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            self.logger.error("Could not delete from {} table in database".format(self.__tablename__ ), exc_info=True)


    @staticmethod
    def get_config():
        db_session = DbSession()
        ccm = None
        try:
            # Should be only one, return last modified
            ccm = db_session.query(ChargerConfigModel) \
                            .order_by(ChargerConfigModel.modified_at.desc()) \
                            .first()
        except Exception as e:
            # Nothing to roll back
            ChargerConfigModel.logger.error("Could not query from {} table in database".format(ChargerConfigModel.__tablename__ ), exc_info=True)
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

class ChargerConfigSchema(Schema):
    """
    ChargerConfigModel Schema
    """
    charger_name = fields.Str(required=True)
    charger_tariff = fields.Float(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)

    SECRET_KEY = fields.Str(dump_only=True)
    WTF_CSRF_SECRET_KEY = fields.Str(dump_only=True)

    httpHost = fields.Str(dump_only=True)
    httpPort = fields.Int(dump_only=True)
    useReloader = fields.Bool(dump_only=True)

    factorWhkm = fields.Integer(dump_only=True)

    autoSessionEnabled = fields.Bool(dump_only=True)
    autoSessionMinutes = fields.Int(dump_only=True)
    autoSessionEnergy = fields.Float(dump_only=True)
    autoSessionCondenseSameOdometer = fields.Bool(dump_only=True)


    pulseLedMin = fields.Int(dump_only=True)
    pulseLedMax = fields.Int(dump_only=True)
    GPIO_Mode = fields.Str(dump_only=True)
    pinLedRed = fields.Int(dump_only=True)
    pinLedGreen = fields.Int(dump_only=True)
    pinLedBlue = fields.Int(dump_only=True)
    pinBuzzer = fields.Int(dump_only=True)

    peakHoursOffPeakEnabled = fields.Bool(dump_only=True)
    peakHoursAllowPeakOnePeriod = fields.Bool(dump_only=True)

    prowlEnabled = fields.Bool(dump_only=True)
    prowlApiKey = fields.Str(dump_only=True)
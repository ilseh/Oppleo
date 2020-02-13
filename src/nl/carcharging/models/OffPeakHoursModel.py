import datetime
import logging

from marshmallow import fields, Schema
from marshmallow.fields import Boolean

from . import db
from sqlalchemy import orm
from nl.carcharging.models.base import Base, DbSession


class OffPeakHoursModel(Base):
    __tablename__ = 'off_peak_hours'

    weekday_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday' ]
    weekday_nl = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag' ]

    id = db.Column(db.Integer, primary_key=True)
    weekday = db.Column(db.String(20))
    holiday = db.Column(db.Date)
    description = db.Column(db.String(100))
    off_peak_start = db.Column(db.Time)
    off_peak_end = db.Column(db.Time)

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.models.OffPeakHoursModel')

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
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session = DbSession()
        db_session.delete(self)
        db_session.commit()


    def weekdayToStr(self, weekday) -> str:
        return self.weekday_en(weekday % len(self.weekday_en))

    # Timestamp of type datetime
    def is_off_peak(self, timestamp) -> bool:
        self.logger.debug('is_off_peak()')
        db_session = DbSession()
        # Weekday?
        r = db_session.query(OffPeakHoursModel) \
                .filter(OffPeakHoursModel.weekday == self.weekdayToStr(timestamp.weekday())) \
                .filter(OffPeakHoursModel.off_peak_start <= timestamp.strftime("%H:%M")) \
                .filter(OffPeakHoursModel.off_peak_end >= timestamp.strftime("%H:%M"))
        if r is not None and len(r) > 0:
            self.logger.debug('DayOfWeek within off-peak')
            return True

        # Is this a public holiday?
        r = db_session.query(OffPeakHoursModel) \
                .filter(OffPeakHoursModel.holiday == timestamp.strftime("%d/%m/%Y")) \
                .filter(OffPeakHoursModel.off_peak_start <= timestamp.strftime("%H:%M")) \
                .filter(OffPeakHoursModel.off_peak_end >= timestamp.strftime("%H:%M"))

        if r is not None and len(r) > 0:
            self.logger.debug('Holiday within off-peak')
            return True

        self.logger.debug('Not within off-peak')
        return False

    def __repr(self):
        return self.to_str()

    def to_str(self):
        return ({
                "id": str(self.id),
                "weekday": (str(self.weekday) if self.weekday is not None else None),
                "holiday": (str(self.holiday) if self.holiday is not None else None),
                "description": str(self.description),
                "off_peak_start": (str(self.off_peak_start) if self.off_peak_start is not None else None),
                "off_peak_end": (str(self.off_peak_end) if self.off_peak_end is not None else None)
            }
        )

class ChargerConfigSchema(Schema):
    """
    ChargerConfigModel Schema
    """
    id = fields.Int(dump_only=True)
    weekday = fields.Str(dump_only=True)
    holiday = fields.Date(dump_only=True)
    description = fields.Str(dump_only=True)
    off_peak_start = fields.Time(dump_only=True)
    off_peak_end = fields.Time(dump_only=True)

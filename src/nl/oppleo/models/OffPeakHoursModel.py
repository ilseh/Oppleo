from datetime import datetime
import logging
from enum import IntEnum
from collections import OrderedDict

from marshmallow import fields, Schema
from marshmallow.fields import Boolean

from sqlalchemy import Column, Integer, Boolean, String, Time, orm, and_, or_, cast, Time, func
from nl.oppleo.models.Base import Base, DbSession

# enum.Enum is not jsonify serializable, IntEnum can be dumped using json.dumps()
class Weekday(IntEnum):
    MONDAY = 0 
    TUESDAY = 1  
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class OffPeakHoursModel(Base):
    logger = logging.getLogger('nl.oppleo.models.OffPeakHoursModel')
    __tablename__ = 'off_peak_hours'

    weekday_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday' ]
    weekday_nl = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag' ]

    month_en = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December' ]
    month_nl = ['Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December' ]

    id = Column(Integer, primary_key=True)
    weekday = Column(String(20))
    holiday_day = Column(Integer)
    holiday_month = Column(Integer)
    holiday_year = Column(Integer)
    recurring = Column(Boolean)
    description = Column(String(100))
    off_peak_start = Column(Time)
    off_peak_end = Column(Time)

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
            self.logger.error("Could not save to {} table in database".format(self.__tablename__ ), exc_info=True)


    def delete(self):
        db_session = DbSession()
        try:
            db_session.delete(self)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            self.logger.error("Could not delete from {} table in database".format(self.__tablename__ ), exc_info=True)

    @staticmethod
    def weekdayToEnStr(weekday) -> str:
        return OffPeakHoursModel.weekday_en[weekday % len(OffPeakHoursModel.weekday_en)]
    @staticmethod
    def weekdayToNlStr(weekday) -> str:
        return OffPeakHoursModel.weekday_nl[weekday % len(OffPeakHoursModel.weekday_nl)]

    def weekdayEnStr(self) -> str:
        return self.weekday_en[self.weekday % len(self.weekday_en)]
    def weekdayNlStr(self) -> str:
        return self.weekday_nl[self.weekday % len(self.weekday_nl)]
    def monthEnStr(self) -> str:
        return self.month_en[(self.holiday_month -1) % len(self.month_en)]
    def monthNlStr(self) -> str:
        return self.month_nl[(self.holiday_month -1) % len(self.month_nl)]

    # Timestamp of type datetime
    def is_off_peak_now(self) -> bool:
        return self.is_off_peak(timestamp=datetime.now())

    # Timestamp of type datetime
    def is_off_peak(self, timestamp) -> bool:
        self.logger.debug('is_off_peak()')
        if not isinstance(timestamp, datetime):
            self.logger.debug('is_off_peak() - timestamp is not of type datetime')
            return False
            
        db_session = DbSession()
        # Weekday?
        r = None
        try:
            r = db_session.query(OffPeakHoursModel) \
                          .filter(OffPeakHoursModel.weekday == OffPeakHoursModel.weekdayToEnStr(timestamp.weekday())) \
                          .filter(OffPeakHoursModel.off_peak_start <= cast(timestamp, Time)) \
                          .filter(OffPeakHoursModel.off_peak_end >= cast(timestamp, Time))
        except Exception as e:
            # Nothing to roll back
            self.logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
        if r is not None and self.get_count(r) > 0:
            self.logger.debug('is_off_peak(): DayOfWeek {} within off-peak'.format(str(timestamp.strftime("%d/%m/%Y, %H:%M:%S"))))
            return True

        # Is this a public holiday?
        r = None
        try:
            r = db_session.query(OffPeakHoursModel) \
                          .filter(
                              or_(
                                  and_(   # Specific holiday
                                      OffPeakHoursModel.holiday_day == int(timestamp.date().day),
                                      OffPeakHoursModel.holiday_month == int(timestamp.date().month),
                                      OffPeakHoursModel.holiday_year == int(timestamp.date().year)
                                  ),
                                  and_(   # Recurring holiday
                                      OffPeakHoursModel.holiday_day == int(timestamp.date().day),
                                      OffPeakHoursModel.holiday_month == int(timestamp.date().month),
                                      OffPeakHoursModel.recurring == True
                                  )
                              )
                              ) \
                          .filter(OffPeakHoursModel.off_peak_start <= cast(timestamp, Time)) \
                          .filter(OffPeakHoursModel.off_peak_end >= cast(timestamp, Time))
        except Exception as e:
            # Nothing to roll back
            self.logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
        if r is not None and self.get_count(r) > 0:
            self.logger.debug('is_off_peak(): Holiday {} within off-peak'.format(str(timestamp.strftime("%d/%m/%Y, %H:%M:%S"))))
            return True

        self.logger.debug('is_off_peak(): {} not within off-peak'.format(str(timestamp.strftime("%d/%m/%Y, %H:%M:%S"))))
        return False


    def is_day(self, dow) -> bool:
        return self.weekday == self.weekday_nl[dow] or \
               self.weekday == self.weekday_en[dow]
    def is_weekday(self) -> bool:
        return self.weekday != None and isinstance(self.weekday, str) and \
               ( self.weekday in self.weekday_nl or self.weekday in self.weekday_en )

    def is_holiday(self) -> bool:
        return not self.is_weekday()

    def is_monday(self) -> bool:
        return self.is_day(Weekday.MONDAY)
    def is_tuesday(self) -> bool:
        return self.is_day(Weekday.TUESDAY)
    def is_wednesday(self) -> bool:
        return self.is_day(Weekday.WEDNESDAY)
    def is_thursday(self) -> bool:
        return self.is_day(Weekday.THURSDAY)
    def is_friday(self) -> bool:
        return self.is_day(Weekday.FRIDAY)
    def is_saturday(self) -> bool:
        return self.is_day(Weekday.SATURDAY)
    def is_sunday(self) -> bool:
        return self.is_day(Weekday.SUNDAY)


    
    @staticmethod
    def get_all():
        db_session = DbSession()
        r = None
        try:
            r = db_session.query(OffPeakHoursModel) \
                          .all()
        except Exception as e:
            # Nothing to roll back
            OffPeakHoursModel.logger.error("Could not query from {} table in database".format(OffPeakHoursModel.__tablename__ ), exc_info=True)
        return r

    
    @staticmethod
    def get_weekday(weekday):
        db_session = DbSession()
        r = None
        try:
            r = db_session.query(OffPeakHoursModel) \
                          .filter(OffPeakHoursModel.weekday == OffPeakHoursModel.weekdayToEnStr(weekday)) \
                          .order_by(OffPeakHoursModel.off_peak_start.asc()) \
                          .all()
        except Exception as e:
            # Nothing to roll back
            OffPeakHoursModel.logger.error("Could not query from {} table in database".format(OffPeakHoursModel.__tablename__ ), exc_info=True)
        return r
        
    @staticmethod
    def get_monday():
        return OffPeakHoursModel.get_weekday(Weekday.MONDAY)
    @staticmethod
    def get_tuesday():
        return OffPeakHoursModel.get_weekday(Weekday.TUESDAY)
    @staticmethod
    def get_wednesday():
        return OffPeakHoursModel.get_weekday(Weekday.WEDNESDAY)
    @staticmethod
    def get_thursday():
        return OffPeakHoursModel.get_weekday(Weekday.THURSDAY)
    @staticmethod
    def get_friday():
        return OffPeakHoursModel.get_weekday(Weekday.FRIDAY)
    @staticmethod
    def get_saturday():
        return OffPeakHoursModel.get_weekday(Weekday.SATURDAY)
    @staticmethod
    def get_sunday():
        return OffPeakHoursModel.get_weekday(Weekday.SUNDAY)

    @staticmethod
    def diffMins(end, start):
        return ((end.hour * 60) + end.minute) - ((start.hour * 60) + start.minute)

    """
        This method returns a representation of peak/ off peak hours during a weekday
        Representation is a list of consecutive entries
        { 
            start: 00:00
            end: 07:00
            offPeak: True/False
        }
    """
    @staticmethod
    def get_representation(weekday):
        section_start_time = datetime.now().time()
        section_start_time = section_start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        op_list = OffPeakHoursModel.get_weekday(weekday)
        if op_list is None or len(op_list) == 0:
            # Return an empty weekday, all hours are peak
            section_end_time = datetime.now().time()
            section_end_time = section_start_time.replace(hour=23, minute=59, second=0, microsecond=0)
            return [{ 'start': section_start_time, 'end': section_end_time, 'diffMins': OffPeakHoursModel.diffMins(section_end_time, section_start_time), 'offPeak': False}]
        repr = []
        for op_entry in op_list:
            if (section_start_time < op_entry.off_peak_start):
                # Gap of peak in between
                repr.append({ 'start': section_start_time, 'end': op_entry.off_peak_start, 'diffMins': OffPeakHoursModel.diffMins(op_entry.off_peak_start, section_start_time), 'offPeak': False})
                # Add off peak period
                repr.append({ 'start': op_entry.off_peak_start, 'end': op_entry.off_peak_end, 'diffMins': OffPeakHoursModel.diffMins(op_entry.off_peak_end, op_entry.off_peak_start), 'offPeak': True})
            if (section_start_time == op_entry.off_peak_start):
                # If previous section was also off-peak
                if len(repr) > 0 and repr[-1]['offPeak']:
                    # extend existing off peak period
                    repr[-1]['offPeak']['end'] = op_entry.off_peak_end
                    repr[-1]['offPeak']['diffMins'] = OffPeakHoursModel.diffMins(repr[-1]['offPeak']['end'], repr[-1]['offPeak']['start'])
                else:
                    # add off peak period
                    repr.append({ 'start': op_entry.off_peak_start, 'end': op_entry.off_peak_end, 'diffMins': OffPeakHoursModel.diffMins(op_entry.off_peak_end, op_entry.off_peak_start), 'offPeak': True})
            if (section_start_time > op_entry.off_peak_start):
                # Double covered! Only limited support for such situations
                if section_start_time > op_entry.off_peak_end:
                    # Completely double covered
                    if repr[-1]['offPeak']:
                        # Section completely doubles previous section.
                        OffPeakHoursModel.logger.debug('OffPeak weekday {} config has entries double covering')
                    else:
                        # Section completely doubles previous peak section, definately not handling this correctly
                        OffPeakHoursModel.logger.warn('OffPeak weekday {} completely double covering entries not interpreted correctly')
                else:
                    # Was previous period off peak?
                    if repr[-1]['offPeak']:
                        # Extend existing off peak period
                        repr[-1]['offPeak']['end'] = op_entry.off_peak_end
                        repr[-1]['offPeak']['diffMins'] = OffPeakHoursModel.diffMins(repr[-1]['offPeak']['end'], repr[-1]['offPeak']['start'])
                    else:
                        # Section partly doubles previous peak section, definately not handling this correctly
                        OffPeakHoursModel.logger.warn('OffPeak weekday {} partly double covering entries not interpreted correctly')
                pass
            # Move to next section
            section_start_time = section_start_time.replace(hour=op_entry.off_peak_end.hour, minute=op_entry.off_peak_end.minute)
        return repr


    @staticmethod
    def get_all_representations_nl():
        repr = OrderedDict()
        for wday in Weekday:
            repr[OffPeakHoursModel.weekday_nl[wday.value]] = OffPeakHoursModel.get_representation(wday.value)
        return repr

    @staticmethod
    def get_all_representations_en():
        repr = OrderedDict()
        for wday in Weekday:
            repr[OffPeakHoursModel.weekday_en[wday.value]] = OffPeakHoursModel.get_representation(wday.value)
        return repr


    def get_count(self, q):
        count = 0
        try:
            count_q = q.statement.with_only_columns([func.count()]).order_by(None)
            count = q.session.execute(count_q).scalar()
        except Exception as e:
            # Nothing to roll back
            self.logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
        return count


    def __repr(self):
        return self.to_str()


    def to_str(self):
        return ({
                "id": str(self.id),
                "weekday": (str(self.weekday) if self.weekday is not None else None),
                "holiday": ((str(self.holiday_day) + '-' + str(self.holiday_month) + '-' + str(self.holiday_year)) \
                             if self.holiday_day is not None and self.holiday_month is not None and self.holiday_year is not None \
                             else None),
                "recurring": str(self.recurring),
                "description": str(self.description),
                "off_peak_start": (str(self.off_peak_start) if self.off_peak_start is not None else None),
                "off_peak_end": (str(self.off_peak_end) if self.off_peak_end is not None else None)
            }
        )


    def test(self):
        ohm = OffPeakHoursModel()
        # test None
        is_op = ohm.is_off_peak(None)
        # test other object (String)
        is_op = ohm.is_off_peak("testing")
        # test now
        ts = datetime.now()
        is_op = ohm.is_off_peak(ts)
        # test today at 22:15
        ts = ts.replace(hour=22, minute=15)
        is_op = ohm.is_off_peak(ts)
        # test today at 23:15
        ts = ts.replace(hour=23, minute=15)
        is_op = ohm.is_off_peak(ts)
        # test jan 1st 2019 as recurring date (is a Tuesday)
        ts = ts.replace(hour=14, minute=15)
        ts = ts.replace(day=1, month=1, year=2019)
        is_op = ohm.is_off_peak(ts)
        # test 1st x-mas day 2020 as recurring date (is a Friday)
        ts = ts.replace(day=25, month=12, year=2019)
        is_op = ohm.is_off_peak(ts)        


class ChargerConfigSchema(Schema):
    """
    ChargerConfigModel Schema
    """
    id = fields.Int(dump_only=True)
    weekday = fields.Str(dump_only=True)
    holiday_day = fields.Int(dump_only=True)
    holiday_month = fields.Int(dump_only=True)
    holiday_year = fields.Int(dump_only=True)
    recurring = fields.Bool(dump_only=True)
    description = fields.Str(dump_only=True)
    off_peak_start = fields.Time(dump_only=True)
    off_peak_end = fields.Time(dump_only=True)

import datetime
import logging

from marshmallow import fields, Schema

from sqlalchemy import orm, Column, Integer, String, DateTime, Float, asc, desc, func
from sqlalchemy import MetaData, Table, select    # For fetchmany

from sqlalchemy.exc import InvalidRequestError

from nl.oppleo.models.Base import Base, DbSession
from nl.oppleo.models.Base import engine    # For fetchmany

from nl.oppleo.exceptions.Exceptions import DbException
import json


class EnergyDeviceMeasureModel(Base):
    """
    EnergyDeviceMeasure Model
    """
    __logger = logging.getLogger('nl.oppleo.models.EnergyDeviceMeasureModel')

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
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            db_session.rollback()
            self.__logger.error("Could not save to {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not save to {} table in database".format(self.__tablename__ ))


    def get_last_saved(self, energy_device_id):
        self.__logger.debug("get_last_saved() energy_device_id {} ".format(energy_device_id))
        last_saved = self.get_last_n_saved(energy_device_id=energy_device_id, n=1)
        if last_saved is not None and isinstance(last_saved, list) and len(last_saved) == 1:
            return last_saved[0]
        self.__logger.debug("get_last_saved() energy_device_id {} - no previous recordings".format(energy_device_id))
        return None


    def get_last_n_saved(self, energy_device_id, n):
        db_session = DbSession()
        edmm = None
        try:
            edmm = db_session.query(EnergyDeviceMeasureModel) \
                             .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                             .order_by(desc(EnergyDeviceMeasureModel.created_at)) \
                             .limit(n) \
                             .all()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            # Nothing to roll back
            self.__logger.error("Could not save to {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not save to {} table in database".format(EnergyDeviceMeasureModel.__tablename__ ))
        return edmm

    def get_last_n_saved_since(self, energy_device_id, since_ts, n=-1):
        db_session = DbSession()
        edmm = None
        try:
            if n == -1:
                edmm = db_session.query(EnergyDeviceMeasureModel) \
                                 .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                                 .filter(EnergyDeviceMeasureModel.created_at >= self.date_str_to_datetime(since_ts)) \
                                 .order_by(desc(EnergyDeviceMeasureModel.created_at)) \
                                 .all()
            else:
                edmm = db_session.query(EnergyDeviceMeasureModel) \
                                 .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                                 .filter(EnergyDeviceMeasureModel.created_at >= self.date_str_to_datetime(since_ts)) \
                                 .order_by(desc(EnergyDeviceMeasureModel.created_at)) \
                                 .limit(n) \
                                 .all()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            # Nothing to roll back
            self.__logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(self.__tablename__ ))
        return edmm

    def get_between(self, energy_device_id, since_ts:datetime=None, until_ts:datetime=None):
        db_session = DbSession()
        edmm = None
        try:
            edmm = db_session.query(EnergyDeviceMeasureModel) \
                                .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                                .filter(EnergyDeviceMeasureModel.created_at >= since_ts) \
                                .filter(EnergyDeviceMeasureModel.created_at <= until_ts) \
                                .order_by(desc(EnergyDeviceMeasureModel.created_at)) \
                                .all()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            # Nothing to roll back
            self.__logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(self.__tablename__ ))
        return edmm

    def get_count_at_timestamp(self, energy_device_id, ts:datetime=None):
        db_session = DbSession()
        edmm = None
        try:
            edmm = db_session.query(func.count(EnergyDeviceMeasureModel.id)) \
                             .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                             .filter(
                                 EnergyDeviceMeasureModel.created_at >= ts if asc else EnergyDeviceMeasureModel.created_at <= ts
                                 ) \
                             .scalar()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            # Nothing to roll back
            self.__logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(self.__tablename__ ))
        return edmm


    """
        Includes all device ids
        Brute force, no sorting or filtering
        https://docs.sqlalchemy.org/en/14/_modules/examples/performance/large_resultsets.html
    """
    def get_all_as_stream(self, callbackFn, batch_size:int=1000):

        try:
            connection = engine.connect()
            edmmt = Table( self.__tablename__, MetaData(), autoload=True, autoload_with=engine )
            edmmQery = select([edmmt]) 
            ResultProxy = connection.execute(edmmQery)
            hasMore = True
            #               .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id)
            while hasMore:
                resultBatch = ResultProxy.fetchmany(batch_size)
                if (resultBatch == []): 
                    hasMore = False
                else:
                    if not callbackFn(resultBatch):
                        return False

        except Exception as e:
            # Nothing to roll back
            self.__logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(self.__tablename__ ))


    def paginate(self, energy_device_id, offset:int=0, limit:int=0, orderColumn:Column=None, orderDir:str=None):
        db_session = DbSession()
        edmm = None
        try:
            if orderColumn is not None:
                edmm = db_session.query(EnergyDeviceMeasureModel) \
                                .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                                .order_by(asc(orderColumn) if orderDir=='asc' else desc(orderColumn)) \
                                .offset(offset) \
                                .limit(limit)
            else: 
                edmm = db_session.query(EnergyDeviceMeasureModel) \
                                .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                                .offset(offset) \
                                .limit(limit)
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            # Nothing to roll back
            self.__logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(self.__tablename__ ))
        return edmm


    def get_count(self):
        db_session = DbSession()
        rows = db_session.query(func.count(EnergyDeviceMeasureModel.id)).scalar()
        return rows


    """
    SELECT edm.created_at, edm.kw_total 
    FROM energy_device_measures edm 
    WHERE edm.created_at in (
        SELECT DISTINCT MAX(created_at) as created_at
        FROM energy_device_measures 
        GROUP BY EXTRACT(YEAR from created_at), EXTRACT(MONTH from created_at)
    ) 
    ORDER BY edm.created_at DESC
    """
    """
    SELECT max(energy_device_measures.created_at) AS created_at 
    FROM energy_device_measures GROUP BY EXTRACT(year FROM energy_device_measures.created_at), EXTRACT(month FROM energy_device_measures.created_at)
    """


    def get_end_month_energy_levels(self, energy_device_id):
        db_session = DbSession()

        try:
            # Find timestamps of last entry per month
            emeTs = db_session.query( \
                        func.max( EnergyDeviceMeasureModel.created_at ) \
                        .label("created_at") 
                        )  \
                    .group_by( \
                        func.extract( "year", EnergyDeviceMeasureModel.created_at ), \
                        func.extract( "month", EnergyDeviceMeasureModel.created_at ) \
                        )
            # Add row data
            emeTs2 = db_session.query( EnergyDeviceMeasureModel ).order_by( asc( EnergyDeviceMeasureModel.created_at ) )
            lastMonthReadingTimestamps = []
            for timestamp in emeTs:
                lastMonthReadingTimestamps.append( timestamp.created_at )
            emeTs2 = emeTs2.filter( EnergyDeviceMeasureModel.created_at.in_( lastMonthReadingTimestamps ) ).all()

        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            # Nothing to roll back
            self.__logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(self.__tablename__ ))

        # Build json return
        lastValue = 0
        eme = []
        for emee in emeTs2:
            eme.append({
                "Month"             : int(emee.created_at.strftime("%m")),
                "Year"              : int(emee.created_at.strftime("%Y")),
                "MonthStart_Kwh"    : lastValue,
                "MonthEnd_Kwh"      : emee.kw_total,
                "MonthUsed_kWh"     : round((emee.kw_total - lastValue)*10)/10
            })
            lastValue = emee.kw_total
        return eme


    def get_usage_since(self, energy_device_id, since_ts):
        self.__logger.debug("get_usage_since() energy_device_id {} since_ts {}".format(energy_device_id, str(since_ts)))
        db_session = DbSession()
        energy_at_ts = 0
        try:
            energy_at_ts = db_session.query(EnergyDeviceMeasureModel) \
                                    .filter(EnergyDeviceMeasureModel.energy_device_id == energy_device_id) \
                                    .filter(EnergyDeviceMeasureModel.created_at <= since_ts) \
                                    .order_by(desc(EnergyDeviceMeasureModel.created_at)) \
                                    .first()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            # Nothing to roll back
            self.__logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(self.__tablename__ ))
        energy_now = self.get_last_saved(energy_device_id)
        if energy_now is None or energy_at_ts is None:
            self.__logger.warn('get_usage_since() - could not get data from database')
            return 0
        energy_used = round((energy_now.kw_total - energy_at_ts.kw_total) *10) /10
        self.__logger.debug('get_usage_since() - since {} usage {}kWh'.format(
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
        except InvalidRequestError as e:
            EnergyDeviceMeasureModel.__cleanupDbSession(db_session, EnergyDeviceMeasureModel.__name__)
        except Exception as e:
            # Nothing to roll back
            EnergyDeviceMeasureModel.__logger.error("Could not query from {} table in database".format(EnergyDeviceMeasureModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(EnergyDeviceMeasureModel.__tablename__ ))
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
                "kwh_l1": str(self.kwh_l1),
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
                "kwh_l1": str(self.kwh_l1),
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

    @staticmethod
    def sto_str(obj):
        d = {}
        for index, fieldname in enumerate(obj._fields):
            if fieldname == 'id':   # hide the id field
                continue
            d[fieldname] = obj._data[index] if fieldname != "created_at" else obj._data[index].strftime("%d/%m/%Y, %H:%M:%S")
        return d

    # convert into dict:
    def to_dict(self):
        return ({
            "energy_device_id": str(self.energy_device_id),
            "created_at": str(self.created_at.strftime("%d/%m/%Y, %H:%M:%S")),
            "kwh_l1": str(self.kwh_l1),
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


    """
        Try to fix any database errors including
            - sqlalchemy.exc.InvalidRequestError: Can't reconnect until invalid transaction is rolled back
    """
    @staticmethod
    def __cleanupDbSession(db_session=None, cn=None):
        logger = logging.getLogger('nl.oppleo.models.Base cleanupSession()')
        logger.debug("Trying to cleanup database session, called from {}".format(cn))
        try:
            db_session.remove()
            if db_session.is_active:
                db_session.rollback()
        except Exception as e:
            logger.debug("Exception trying to cleanup database session from {}".format(cn), exc_info=True)


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

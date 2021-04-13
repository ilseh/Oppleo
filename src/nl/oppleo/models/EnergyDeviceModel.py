from marshmallow import fields, Schema

from nl.oppleo.models.Base import Base, DbSession
from nl.oppleo.exceptions.Exceptions import DbException

from sqlalchemy import orm, func, Column, String, Integer, Boolean, desc
from sqlalchemy.exc import InvalidRequestError


class EnergyDeviceModel(Base):
    """
    EnergyDevice Model
    """

    # table name
    __tablename__ = 'energy_device'

    energy_device_id = Column(String(100), primary_key=True)
    port_name = Column(String(100))
    slave_address = Column(Integer)
    baudrate = Column(Integer)
    bytesize = Column(Integer)
    parity = Column(String(1))
    stopbits = Column(Integer)
    serial_timeout = Column(Integer)
    debug = Column(Boolean)
    mode = Column(String(10))
    close_port_after_each_call = Column(Boolean)
    modbus_config = Column(String(100))
    device_enabled = Column(Boolean)

    def __init__(self, data):
        pass


    # sqlalchemy calls __new__ not __init__ on reconstructing from database. Decorator to call this method
    @orm.reconstructor   
    def init_on_load(self):
        pass


    def save(self):
        db_session = DbSession()
        try:
            db_session.add(self)
            db_session.commit()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            db_session.rollback()
            self.logger.error("Could not save to {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not save to {} table in database".format(self.__tablename__ ))


    # no delete, only update
    """
    def delete(self):
        db_session = DbSession()
        try:
            db_session.delete(self)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            self.logger.error("Could not delete from {} table in database".format(self.__tablename__ ), exc_info=True)

    """

    @staticmethod
    def get():
        db_session = DbSession()
        edm = None
        try:
            edm =  db_session.query(EnergyDeviceModel) \
                             .order_by(desc(EnergyDeviceModel.energy_device_id)) \
                             .first()
        except InvalidRequestError as e:
            EnergyDeviceModel.__cleanupDbSession(db_session, EnergyDeviceModel.__class__)
        except Exception as e:
            # Nothing to roll back
            EnergyDeviceModel.logger.error("Could not get energy device from table {} in database ({})".format(EnergyDeviceModel.__tablename__, str(e)), exc_info=True)
            raise DbException("Could not get energy device from table {} in database ({})".format(EnergyDeviceModel.__tablename__, str(e)))
        return edm

    def __repr(self):
        return '<id {}>'.format(self.id)

    def get_count(self, q):
        count = 0
        try:
            count_q = q.statement.with_only_columns([func.count()]).order_by(None)
            count = q.session.execute(count_q).scalar()
        except Exception as e:
            self.logger.error("Could not query from {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(self.__tablename__ ))
        return count


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



class EnergyDeviceSchema(Schema):
    """
    Energy Device Schema
    """
    energy_device_id = fields.Str(required=True)
    port_name = fields.Str(dump_only=True)
    slave_address = fields.Int(dump_only=True)
    baudrate = fields.Int(dump_only=True)
    bytesize = fields.Int(dump_only=True)
    parity = fields.Str(dump_only=True)
    stopbits = fields.Int(dump_only=True)
    serial_timeout = fields.Int(dump_only=True)
    debug = fields.Bool(dump_only=True)
    mode = fields.Str(dump_only=True)
    close_port_after_each_call = fields.Bool(dump_only=True)
    modbus_config = fields.Str(dump_only=True)
    device_enabled = fields.Bool(dump_only=True)


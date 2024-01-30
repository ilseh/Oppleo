from datetime import datetime
import logging
import json

from marshmallow import fields, Schema

from nl.oppleo.models.Base import Base, DbSession
from nl.oppleo.exceptions.Exceptions import DbException

from sqlalchemy import orm, Column, Integer, String, Boolean, DateTime
from sqlalchemy.exc import InvalidRequestError



class AccesslogModel(Base):
    __tablename__ = 'accesslog'
    __logger = None
    
    id = Column(Integer, primary_key=True)
    IPv4 = Column(String(20))       # IP address
    last_seen = Column(DateTime)    # Reset at any visit
    login = Column(Boolean)         # True is any visit was a succesful login from this IP
    visits = Column(Integer)        # Total number of visits
    days = Column(Integer)          # Individual days

    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__module__)


    # sqlalchemy calls __new__ not __init__ on reconstructing from database. Decorator to call this method
    @orm.reconstructor   
    def init_on_load(self):
        # Make sure the init does not reset any values, those are taken from the db
        self.__init__()


    def set(self, data):
        for key in data:
            setattr(self, key, data.get(key))
        self.allow = data.get('allow', False)

    def save(self):
        db_session = DbSession()
        try:
            db_session.add(self)
            db_session.commit()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__module__)
        except Exception as e:
            db_session.rollback()
            self.__logger.error("Could not save to {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not save to {} table in database".format(self.__tablename__ ))


    def update(self):
        db_session = DbSession()
        try:
            db_session.commit()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__module__)
        except Exception as e:
            db_session.rollback()
            self.__logger.error("Could not commit (update) to {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not commit (update) to {} table in database".format(self.__tablename__ ))


    def delete(self):
        db_session = DbSession()
        try:
            db_session.delete(self)
            db_session.commit()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__module__)
        except Exception as e:
            db_session.rollback()
            self.__logger.error("Could not delete from {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not delete from {} table in database".format(self.__tablename__ ))


    @staticmethod
    def get_all():
        db_session = DbSession()
        alm = None
        try:
            alm = db_session.query(AccesslogModel) \
                                   .all()
        except InvalidRequestError as e:
            AccesslogModel.__cleanupDbSession(db_session, AccesslogModel.__class__.__module__)
        except Exception as e:
            # Nothing to roll back
            AccesslogModel.__logger.error("Could not query from {} table in database".format(AccesslogModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(AccesslogModel.__tablename__ ))
        return alm

    def __repr(self):
        return '<id {}>'.format(self.id)

    def to_str(self):
        return ({
                "id": str(self.id),
                "IPv4": self.IPv4,
                "last_seen": (str(self.created_at.strftime("%d/%m/%Y, %H:%M:%S")) if self.created_at is not None else None),
                "login": str(self.login),
                "visits": str(self.visits),
                "days": str(self.days)
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


class AccesslogSchema(Schema):
    """
    Accesslog Schema
    """
    id = fields.Str(required=True)
    IPv4 = fields.Str(required=True)
    last_seen = fields.DateTime(dump_only=True)
    login = fields.Bool(dump_only=True)
    visits = fields.Str(required=True)
    days = fields.Str(required=True)


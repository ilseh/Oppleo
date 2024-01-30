from datetime import datetime
import logging
import json

from marshmallow import fields, Schema

from nl.oppleo.models.Base import Base, DbSession
from nl.oppleo.exceptions.Exceptions import DbException

from sqlalchemy import orm, Column, Integer, String, DateTime, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.exc import InvalidRequestError
from sqlalchemy_json import mutable_json_type

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig

oppleoSystemConfig = OppleoSystemConfig()

"""
    JSON in sqlalchemy
    https://amercader.net/blog/beware-of-json-fields-in-sqlalchemy/
"""

class KeyValueStoreModel(Base):
    __tablename__ = 'keyvaluestores'
    __logger = None

    __table_args__ = (
        PrimaryKeyConstraint('kvstore', 'scope', 'key'),
        UniqueConstraint('kvstore', 'scope', 'key', name='unique_combination_commit'),
    )    
    kvstore = Column(String(256))
    scope = Column(String(256))
    key = Column(String(256))
    value = Column(mutable_json_type(dbtype=JSONB, nested=True))
    created_at = Column(DateTime)
    modified_at = Column(DateTime)


    def __init__(self, **kwargs):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(self.__class__.__module__))    
        for kw in kwargs:
            self.set( { kw: kwargs[kw] } )


    # sqlalchemy calls __new__ not __init__ on reconstructing from database. Decorator to call this method
    @orm.reconstructor   
    def init_on_load(self):
        # Make sure the init does not reset any values, those are taken from the db
        self.__init__()


    def set(self, data):
        for key in data:
            setattr(self, key, data.get(key))
        self.allow = data.get('allow', False)
        self.created_at = data.get('created_at', datetime.now())
        self.modified_at = data.get('modified_at', datetime.now())


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
    def get_value(kvstore:str=None, scope:str=None, key:str=None):
        db_session = DbSession()
        kvsm = None
        try:
            kvsm = db_session.query(KeyValueStoreModel) \
                             .filter(KeyValueStoreModel.kvstore == kvstore) \
                             .filter(KeyValueStoreModel.scope == scope) \
                             .filter(KeyValueStoreModel.key == key) \
                             .first()
        except InvalidRequestError as e:
            KeyValueStoreModel.__cleanupDbSession(db_session, KeyValueStoreModel.__class__.__module__)
        except Exception as e:
            # Nothing to roll back
            KeyValueStoreModel.__logger.error("Could not query from {} table in database".format(KeyValueStoreModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(KeyValueStoreModel.__tablename__ ))
        return kvsm


    @staticmethod
    def get_scope(kvstore:str=None, scope:str=None):
        db_session = DbSession()
        kvsm = None
        try:
            kvsm = db_session.query(KeyValueStoreModel) \
                             .filter(KeyValueStoreModel.kvstore == kvstore) \
                             .filter(KeyValueStoreModel.scope == scope) \
                             .all()
        except InvalidRequestError as e:
            KeyValueStoreModel.__cleanupDbSession(db_session, KeyValueStoreModel.__class__.__module__)
        except Exception as e:
            # Nothing to roll back
            KeyValueStoreModel.__logger.error("Could not query from {} table in database".format(KeyValueStoreModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(KeyValueStoreModel.__tablename__ ))
        return kvsm


    @staticmethod
    def get_kvstore(kvstore:str=None):
        db_session = DbSession()
        kvsm = None
        try:
            kvsm = db_session.query(KeyValueStoreModel) \
                             .filter(KeyValueStoreModel.kvstore == kvstore) \
                             .all()
        except InvalidRequestError as e:
            KeyValueStoreModel.__cleanupDbSession(db_session, KeyValueStoreModel.__class__.__module__)
        except Exception as e:
            # Nothing to roll back
            KeyValueStoreModel.__logger.error("Could not query from {} table in database".format(KeyValueStoreModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(KeyValueStoreModel.__tablename__ ))
        return kvsm


    @staticmethod
    def get_all():
        db_session = DbSession()
        rfidm = None
        try:
            rfidm = db_session.query(KeyValueStoreModel) \
                              .all()
        except InvalidRequestError as e:
            KeyValueStoreModel.__cleanupDbSession(db_session, KeyValueStoreModel.__class__.__module__)
        except Exception as e:
            # Nothing to roll back
            KeyValueStoreModel.__logger.error("Could not query from {} table in database".format(KeyValueStoreModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(KeyValueStoreModel.__tablename__ ))
        return rfidm


    """
        Submit a single object or a list of objects. Objects are of type KeyValueStoreModel
    """
    @staticmethod
    def save_scope(kvstore:str=None, scope:str=None, key_value_obj:object=None, key_value_list:list=None):
        # Make sure all are in this kvstore scope
        if key_value_list is not None:
            for kvs in key_value_list:
                kvs.kvstore = kvstore if kvstore is not None else kvs.kvstore
                kvs.scope = scope if scope is not None else kvs.scope
        if key_value_obj is not None:
            key_value_obj.kvstore = kvstore if kvstore is not None else key_value_obj.kvstore
            key_value_obj.scope = scope if scope is not None else key_value_obj.scope
        db_session = DbSession()
        try:
            if key_value_list is not None:
                db_session.add_all(key_value_list)
            if key_value_obj is not None:
                db_session.add(key_value_obj)
            db_session.commit()
        except InvalidRequestError as e:
            KeyValueStoreModel.__cleanupDbSession(db_session, KeyValueStoreModel.__class__.__module__)
        except Exception as e:
            db_session.rollback()
            KeyValueStoreModel.__logger.error("Could not save to {} table in database".format(KeyValueStoreModel.__tablename__ ), exc_info=True)
            raise DbException("Could not save to {} table in database".format(KeyValueStoreModel.__tablename__ ))


    def __repr(self):
        return '<id {}>'.format(self.rfid)

    def to_str(self):
        return ({
                "kv_store": str(self.kv_store),
                "kv_scope": str(self.kv_scope),
                "kv_key": str(self.kv_key),
                "kv_value": str(self.kv_value),
                "kv_created_at": (str(self.kv_created_at.strftime("%d/%m/%Y, %H:%M:%S")) if self.created_at is not None else None),
                "kv_modified_at": (str(self.kv_modified_at.strftime("%d/%m/%Y, %H:%M:%S")) if self.last_used_at is not None else None)
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

 
class RfidSchema(Schema):
    """
    KeyValueStore Schema
    """
    kvstore = fields.Str(required=True)
    scope = fields.Str(required=True)
    key = fields.Str(required=True)
    value = fields.Str(dump_only=True)  # JSONB
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)


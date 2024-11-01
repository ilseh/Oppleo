from typing import Union
import datetime
from logging import Logger, getLogger

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


from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.models.Base import Base, DbSession
from nl.oppleo.exceptions.Exceptions import DbException

from nl.oppleo.models.User import User

from webauthn.registration.verify_registration_response import VerifiedRegistration
from webauthn.helpers.structs import PublicKeyCredentialDescriptor
from webauthn.helpers import bytes_to_base64url, base64url_to_bytes

oppleoSystemConfig = OppleoSystemConfig()

""" 
    
"""

class WebAuthNCredentialModel(Base):
    __logger:Union[Logger, None] = None
    __tablename__ = 'webauthn_credentials'

    credential_id = Column(String(256), primary_key=True)
    credential_name = Column(String(100))
    created_at = Column(DateTime)  
    aaguid = Column(String(100))

    # Username of the owner User
    credential_owner = Column(String)

    credential_backed_up = Column(Boolean) 
    credential_device_type = Column(String(100))
    credential_public_key = Column(String(256))
    credential_type = Column(String(100))
    fmt = Column(String(100))
    sign_count = Column(Integer) 

    user_verified = Column(Boolean) 

    modified_at = Column(DateTime)        # Last config update

    def __init__(self):
        if self.__logger is None:
            self.__logger = getLogger(self.__class__.__module__)
            self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(self.__class__.__module__))        
        self.__logger.debug('.init()')

    # sqlalchemy calls __new__ not __init__ on reconstructing from database. Decorator to call this method
    @orm.reconstructor   
    def init_on_load(self):
        if self.__logger is None:
            self.__logger = getLogger(self.__class__.__module__)
            self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(self.__class__.__module__))        
        self.__logger.debug('.init_on_load()')
        self.__init__()

    def set(self, data:dict):
        self.__logger.debug('.set()')
        for key in data:
            self.__logger.debug('.set() key:{} value:{}'.format(key, data.get(key)))
            setattr(self, key, data.get(key))
        self.modified_at = datetime.datetime.now()
        self.__logger.debug('.set() modified_at:{}'.format(self.modified_at))


    @staticmethod
    def create(verifiedRegistration:Union[VerifiedRegistration,None]=None, name:Union[str, None]=None, user:Union[User,None]=None):

        logger = getLogger('nl.oppleo.models.WebAuthNCredentialModel')
        logger.debug(".create()")

        if verifiedRegistration is None or user is None:
            logger.debug("No verifiedRegistration or user.")
            return None
        
        newCred = WebAuthNCredentialModel()

        newCred.credential_owner = user.username

        if type(verifiedRegistration.credential_id) is bytes:
            newCred.credential_id = bytes_to_base64url(val=verifiedRegistration.credential_id)
        else:
            newCred.credential_id = verifiedRegistration.credential_id
        if name is not None and name != "":
            newCred.credential_name = name
        else:
            # Default name
            newCred.credential_name = "Key {}".format(
                    ( WebAuthNCredentialModel.getRegisteredCredentialCount(credential_owner=user.username) + 1 )
                )
            pass

        newCred.aaguid = verifiedRegistration.aaguid

        newCred.credential_backed_up = verifiedRegistration.credential_backed_up
        newCred.credential_device_type = verifiedRegistration.credential_device_type
        if type(verifiedRegistration.credential_public_key) is bytes:
            newCred.credential_public_key = bytes_to_base64url(val=verifiedRegistration.credential_public_key)
        else:
            newCred.credential_public_key = verifiedRegistration.credential_public_key
        newCred.credential_type = verifiedRegistration.credential_type
        newCred.fmt = verifiedRegistration.fmt
        newCred.sign_count = verifiedRegistration.sign_count
        newCred.user_verified = verifiedRegistration.user_verified

        newCred.save()

        logger.debug("Created!")

        return newCred


    @property
    def credential_id_bytes(self):
        return  base64url_to_bytes(val=self.credential_id)


    @property
    def credential_public_key_bytes(self):
        return  base64url_to_bytes(val=self.credential_public_key)


    @staticmethod
    def get(credential_owner:Union[str,None]=None, credential_id:Union[str, None]=None):

        logger = getLogger('nl.oppleo.models.WebAuthNCredentialModel')
        logger.debug(".get()")

        if credential_id is None or credential_owner is None:
            logger.debug("No credential_id or credential_owner.")
            return None
        
        registeredCredential = None
        db_session = DbSession()
        try:
            registeredCredential = db_session.query(WebAuthNCredentialModel) \
                                                .filter(WebAuthNCredentialModel.credential_owner == str(credential_owner)) \
                                                .filter(WebAuthNCredentialModel.credential_id == str(credential_id)) \
                                                .first()
        except InvalidRequestError as e:
            WebAuthNCredentialModel.__cleanupDbSession(db_session, WebAuthNCredentialModel.__class__.__module__)
        except Exception as e:
            # Nothing to roll back
            WebAuthNCredentialModel.__logger.error("Could not query from {} table in database".format(WebAuthNCredentialModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(WebAuthNCredentialModel.__tablename__ ))

        return registeredCredential


    """
        Set a single variable
    """
    def setAndSave(self, key, value, allowed=None):
        self.__logger.debug('.setAndSave() key:{} value:{} range:{}'.format(key, value, allowed))
        curVal = getattr(self, key)
        self.__logger.debug('.setAndSave() curVal:{}'.format(curVal))
        if not isinstance(value, type(curVal)):
            self.__logger.debug(".setAndSave() {} TypeError: {} must be type {}".format(key, type(curVal)))
            raise TypeError("{} must be type {}".format(key, type(curVal)))
        self.__logger.debug('.setAndSave() no TypeError')
        if allowed is not None and value not in allowed:
            self.__logger.debug(".setAndSave() {} ValueError: value {} of key {} not within range {}".format(value, key, allowed))
            raise ValueError("{} value {} of key {} not within range {}".format(value, key, allowed))
        self.__logger.debug('.setAndSave() no ValueError')
        setattr(self, key, value)
        self.__logger.debug('.setAndSave() curVal:{} getattr(self, key)={}'.format(curVal, getattr(self, key)))
        if curVal != getattr(self, key):
            # Value changed
            self.modified_at = datetime.datetime.now()
            self.save()

    def save(self):
        self.__logger.debug(".save()")
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
            self.__logger.error(".save() - Could not commit to {} table in database".format(self.__tablename__ ), exc_info=True)
            self.__cleanupDbSession(db_session, self.__class__.__module__)
        except Exception as e:
            db_session.rollback()
            self.__logger.error(".save() - Could not commit to {} table in database".format(self.__tablename__ ), exc_info=True)
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
            self.__cleanupDbSession(db_session, self.__class__.__module__)
        except Exception as e:
            db_session.rollback()
            self.__logger.error("Could not delete from {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not delete from {} table in database".format(self.__tablename__ ))

    """
        Returns a count of registered credentials for this user
    """
    @staticmethod
    def getRegisteredCredentialCount(credential_owner:Union[str, None]=None) -> int:
        WebAuthNCredentialModel.__logger = getLogger('nl.oppleo.models.WebAuthNCredentialModel')

        WebAuthNCredentialModel.__logger.debug(".getRegisteredCredentialCount()")

        db_session = DbSession()
        credentialRegistrations = []
        try:
            credentialRegistrations = db_session.query(WebAuthNCredentialModel) \
                                                .filter(WebAuthNCredentialModel.credential_owner == str(credential_owner)) \
                                                .all()
        except InvalidRequestError as e:
            WebAuthNCredentialModel.__cleanupDbSession(db_session, WebAuthNCredentialModel.__class__.__module__)
        except Exception as e:
            # Nothing to roll back
            WebAuthNCredentialModel.__logger.error("Could not query from {} table in database".format(WebAuthNCredentialModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(WebAuthNCredentialModel.__tablename__ ))

        return len(credentialRegistrations)


    """
        Returns if the user has registered credentials
    """
    @staticmethod
    def hasRegisteredCredentials(credential_owner:Union[str, None]=None) -> bool:
        WebAuthNCredentialModel.__logger = getLogger('nl.oppleo.models.WebAuthNCredentialModel')

        return WebAuthNCredentialModel.getRegisteredCredentialCount(credential_owner=credential_owner) > 0

    """
        Returns a list of registered WebAuthNCredentialModel for this user
    """
    @staticmethod
    def getRegisteredCredentialRegistrations(credential_owner:Union[str, None]=None):
        WebAuthNCredentialModel.__logger = getLogger('nl.oppleo.models.WebAuthNCredentialModel')

        WebAuthNCredentialModel.__logger.debug(".getRegisteredCredentialRegistrations()")

        db_session = DbSession()
        credentialRegistrations = []
        try:
            credentialRegistrations = db_session.query(WebAuthNCredentialModel) \
                                                .filter(WebAuthNCredentialModel.credential_owner == str(credential_owner)) \
                                                .all()
        except InvalidRequestError as e:
            WebAuthNCredentialModel.__cleanupDbSession(db_session, WebAuthNCredentialModel.__class__.__module__)
        except Exception as e:
            # Nothing to roll back
            WebAuthNCredentialModel.__logger.error("Could not query from {} table in database".format(WebAuthNCredentialModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(WebAuthNCredentialModel.__tablename__ ))

        return credentialRegistrations

    """
        Returns a list of registered credential_ids for this user
    """
    @staticmethod
    def getRegisteredCredentials(credential_owner:Union[str, None]=None):
        WebAuthNCredentialModel.__logger = getLogger('nl.oppleo.models.WebAuthNCredentialModel')

        WebAuthNCredentialModel.__logger.debug(".getRegisteredCredentials()")

        credentialRegistrations = WebAuthNCredentialModel.getRegisteredCredentialRegistrations(credential_owner=credential_owner)

        registeredCredentials = []
        for credential in credentialRegistrations:
            publicKeyCredentialDescriptor = PublicKeyCredentialDescriptor(id=credential.credential_id_bytes)
#            publicKeyCredentialDescriptor = PublicKeyCredentialDescriptor(id=bytes(credential.credential_id_bytes, 'utf-8'))
            registeredCredentials.append( publicKeyCredentialDescriptor )
        return registeredCredentials


    """
        Returns the public key and the username for a registered credential_id
    """
    @staticmethod
    def getRegisteredCredential(credential_id:Union[str, None]=None, username:Union[str, None]=None):
        WebAuthNCredentialModel.__logger = getLogger('nl.oppleo.models.WebAuthNCredentialModel')
        WebAuthNCredentialModel.__logger.debug(".getRegisteredCredential()")

        if credential_id is None:
            WebAuthNCredentialModel.__logger.debug("No credential_id provided (None)")
            return

        db_session = DbSession()
        credentialRegistration = None
        try:
            if username is None:
                credentialRegistration = db_session.query(WebAuthNCredentialModel) \
                                                .filter(WebAuthNCredentialModel.credential_id == str(credential_id)) \
                                                .first()
            else:
                credentialRegistration = db_session.query(WebAuthNCredentialModel) \
                                                .filter(WebAuthNCredentialModel.credential_id == str(credential_id)) \
                                                .filter(WebAuthNCredentialModel.credential_owner == str(username)) \
                                                .first()
        except InvalidRequestError as e:
            WebAuthNCredentialModel.__cleanupDbSession(db_session, WebAuthNCredentialModel.__class__.__module__)
        except Exception as e:
            # Nothing to roll back
            WebAuthNCredentialModel.__logger.error("Could not query from {} table in database".format(WebAuthNCredentialModel.__tablename__ ), exc_info=True)
            raise DbException("Could not query from {} table in database".format(WebAuthNCredentialModel.__tablename__ ))

        return credentialRegistration


    def __repr(self):
        return self.to_str()


    def to_str(self):
        return ({
                "credential_id": str(self.credential_id),
                "name": str(self.credential_name),
                "aaguid": str(self.aaguid),
                "credential_device_type": str(self.credential_device_type),
                "credential_type": str(self.credential_type),
                "registered": (str(self.created_at.strftime("%d/%m/%Y, %H:%M:%S")) if self.created_at is not None else None),
                "modified_at": (str(self.modified_at.strftime("%d/%m/%Y, %H:%M:%S")) if self.modified_at is not None else None)
            }
        )

    def to_dict(self):
        me = {}
        me["credential_id"] = str(self.credential_id)
        me["name"] = "" if self.credential_name is None else str(self.credential_name)
        me["aaguid"] = str(self.aaguid)
        me["credential_device_type"] = str(self.credential_device_type)
        me["credential_type"] = str(self.credential_type)
        me["registered"] = (str(self.created_at.strftime("%d/%m/%Y, %H:%M:%S")) if self.created_at is not None else None)
        me["modified_at"] = (str(self.modified_at.strftime("%d/%m/%Y, %H:%M:%S")) if self.modified_at is not None else None)
        return me


    """
        Try to fix any database errors including
            - sqlalchemy.exc.InvalidRequestError: Can't reconnect until invalid transaction is rolled back
    """
    @staticmethod
    def __cleanupDbSession(db_session=None, cn=None):

        logger = getLogger('nl.oppleo.models.WebAuthNCredentialModel')
        logger.debug(".__cleanupDbSession() - Trying to cleanup database session, called from {}".format(cn))
        try:
            db_session.remove()
            if db_session.is_active:
                db_session.rollback()
        except Exception as e:
            logger.debug(".__cleanupDbSession() - Exception trying to cleanup database session from {}".format(cn), exc_info=True)



class WebAuthNCredentialModelSchema(Schema):
    """
    WebAuthNCredentialModel Schema
    """
    credential_id = fields.Str(required=True)
    name = fields.Str(dump_only=True)
    registration_timestamp = fields.DateTime(dump_only=True)
    aaguid = fields.Str(dump_only=True)

    credential_backed_up = fields.Bool(dump_only=True)
    credential_device_type = fields.Str(dump_only=True)
    credential_public_key = fields.Str(dump_only=True)
    credential_type = fields.Str(dump_only=True)
    fmt = fields.Str(dump_only=True)
    sign_count = fields.Int(dump_only=True)

    user_verified = fields.Bool(dump_only=True)

    modified_at = fields.DateTime(dump_only=True)


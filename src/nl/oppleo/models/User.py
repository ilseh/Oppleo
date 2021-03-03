from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import orm, Column, String, Boolean
from sqlalchemy.exc import InvalidRequestError

import logging

from nl.oppleo.models.Base import Base, DbSession
from nl.oppleo.exceptions.Exceptions import DbException

# generate_password_hash(password, method='sha256')

class User(Base):
    """
    """
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    password = Column(String)
    authenticated = Column(Boolean, default=False)

    def __init__(self, username=None, password=None, authenticated=None):
        self.__logger = logging.getLogger('nl.oppleo.models.User')
        # If the variables are already initialized by the reconstructor, let them be
        if self.username is None and self.password is None:
            self.username = username
            self.password = password
            self.authenticated = authenticated

    # sqlalchemy calls __new__ not __init__ on reconstructing from database. Decorator to call this method
    @orm.reconstructor   
    def init_on_load(self):
        self.__init__()

    @staticmethod
    def get(username):
        db_session = DbSession()
        user = None
        try:
            # Should be only one, return last modified
            user = db_session.query(User) \
                            .filter(User.username == username) \
                            .first()
        except InvalidRequestError as e:
            User.__cleanupDbSession(db_session, User.__class__.__name__)
        except Exception as e:
            # Nothing to roll back
            User.__logger.error("Could not query {} table in database".format(User.__tablename__ ), exc_info=True)
            raise DbException("Could not query {} table in database".format(User.__tablename__ ))
        return user


    def save(self) -> None:
        db_session = DbSession()
        try:
            db_session.add(self)
            db_session.commit()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            db_session.rollback()
            self.__logger.error("Could not commit to {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not commit to {} table in database".format(self.__tablename__ ))

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.username

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    # Delete this user
    def delete(self):
        db_session = DbSession()
        try:
            # Should be only one
            num_rows_deleted = db_session.query(User) \
                                         .filter(User.username == self.username) \
                                         .delete()
            db_session.commit()
        except InvalidRequestError as e:
            self.__cleanupDbSession(db_session, self.__class__.__name__)
        except Exception as e:
            db_session.rollback()
            self.__logger.error("Could not commit to {} table in database".format(self.__tablename__ ), exc_info=True)
            raise DbException("Could not commit to {} table in database".format(self.__tablename__ ))

    # Delete all users
    @staticmethod
    def delete_all():
        db_session = DbSession()
        try:
            # Should be only one
            num_rows_deleted = db_session.query(User) \
                                         .delete()
            db_session.commit()
        except InvalidRequestError as e:
            User.__cleanupDbSession(db_session, User.__class__.__name__)
        except Exception as e:
            db_session.rollback()
            User.__logger.error("Could not commit to {} table in database".format(User.__tablename__ ), exc_info=True)
            raise DbException("Could not commit to {} table in database".format(User.__tablename__ ))


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

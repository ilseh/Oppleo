from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import orm, Column, String, Boolean

import logging

from nl.carcharging.models.Base import Base, DbSession
from nl.carcharging.config.WebAppConfig import WebAppConfig

# generate_password_hash(password, method='sha256')

class User(Base):
    """
    """
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    password = Column(String)
    authenticated = Column(Boolean, default=False)

    def __init__(self, username=None, password=None, authenticated=False):
        self.logger = logging.getLogger('nl.carcharging.models.User')
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
        # Should be only one, return last modified
        user = db_session.query(User) \
                         .filter(User.username == username) \
                         .first()
        return user

    def save(self) -> None:
        db_session = DbSession()
        db_session.add(self)
        db_session.commit()

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

    # Delete all users
    @staticmethod
    def delete_all():
        db_session = DbSession()
        try:
            # Should be only one, return last modified
            num_rows_deleted = db_session.query(User) \
                                         .delete()
            db_session.commit()
        except:
            db_session.rollback()



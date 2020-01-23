from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

from config import WebAppConfig

engine = create_engine(os.getenv(WebAppConfig.PARAM_DB_URL), pool_pre_ping=True)

session_factory = sessionmaker(bind=engine)
DbSession = scoped_session(session_factory)

Base = declarative_base()

WebAppConfig.sqlalchemy_engine = engine
WebAppConfig.sqlalchemy_session_factory = session_factory
WebAppConfig.sqlalchemy_session = DbSession

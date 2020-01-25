from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from nl.carcharging.config.WebAppConfig import WebAppConfig

print(' 2 WebAppConfig.PARAM_DB_URL: %s ' % WebAppConfig.DATABASE_URL)
print(' 2 ini: %s ' % WebAppConfig.ini_settings)

if (WebAppConfig.ini_settings == None):
    WebAppConfig.loadConfig()

print(' 3 WebAppConfig.PARAM_DB_URL: %s ' % WebAppConfig.DATABASE_URL)
print(' 3 ini: %s ' % WebAppConfig.ini_settings)

engine = create_engine(WebAppConfig.DATABASE_URL, pool_pre_ping=True)

session_factory = sessionmaker(bind=engine)
DbSession = scoped_session(session_factory)

Base = declarative_base()

WebAppConfig.sqlalchemy_engine = engine
WebAppConfig.sqlalchemy_session_factory = session_factory
WebAppConfig.sqlalchemy_session = DbSession

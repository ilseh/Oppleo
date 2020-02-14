from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from nl.carcharging.config.WebAppConfig import WebAppConfig

if (WebAppConfig.ini_settings == None):
    WebAppConfig.loadConfig()

engine = create_engine(
            WebAppConfig.DATABASE_URL,
            pool_size=5,                # Default is 5 - min conns kept in the pool
            max_overflow=10,            # Default is 10 - max conns handed out
#            timeout=5,                  # Default 30 - time to give up connection
            pool_pre_ping=True,         # validate connection before use
            pool_recycle=3600           # recycle connections after one hour
            )

session_factory = sessionmaker(bind=engine)
DbSession = scoped_session(session_factory)

Base = declarative_base()

WebAppConfig.sqlalchemy_engine = engine
WebAppConfig.sqlalchemy_session_factory = session_factory
WebAppConfig.sqlalchemy_session = DbSession

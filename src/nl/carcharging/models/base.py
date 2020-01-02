from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

engine = create_engine(os.getenv('DATABASE_URL'), pool_pre_ping=True)


session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

Base = declarative_base()
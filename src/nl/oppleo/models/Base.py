import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from nl.oppleo.config.OppleoConfig import OppleoConfig

if (OppleoConfig.ini_settings == None):
    OppleoConfig.loadConfig()

engine = create_engine(
            OppleoConfig.DATABASE_URL,
            pool_size=5,                # Default is 5 - min conns kept in the pool
            max_overflow=10,            # Default is 10 - max conns handed out
#            timeout=5,                  # Default 30 - time to give up connection
            pool_pre_ping=True,         # validate connection before use
            pool_recycle=3600           # recycle connections after one hour
            )

session_factory = sessionmaker(bind=engine)
DbSession = scoped_session(session_factory)

Base = declarative_base()

OppleoConfig.sqlalchemy_engine = engine
OppleoConfig.sqlalchemy_session_factory = session_factory
OppleoConfig.sqlalchemy_session = DbSession

def init_db():
    logger = logging.getLogger('nl.oppleo.models.Base init_db()')

    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import nl.oppleo.models.ChargerConfigModel
    import nl.oppleo.models.ChargeSessionModel
    import nl.oppleo.models.EnergyDeviceMeasureModel
    import nl.oppleo.models.EnergyDeviceModel
    import nl.oppleo.models.OffPeakHoursModel
    import nl.oppleo.models.RfidModel
    import nl.oppleo.models.User
    try:
        Base.metadata.create_all(bind=engine)
    except:
        logger.error('COULD NOT CONNECT TO DATABASE!!!')
        raise SystemExit

init_db()


from marshmallow import fields, Schema
import datetime
import logging
from . import db
from sqlalchemy import func
from nl.carcharging.models.base import Base, Session


class SessionModel(Base):
    """
    Session Model
    """

    # table name
    __tablename__ = 'session'             # -> sessions

    id = db.Column(db.Integer, primary_key=True)
    rfid = db.Column(db.String(128), nullable=False)
    energy_device_id = db.Column(db.String(128), nullable=False)
    start_value = db.Column(db.Float)
    end_value = db.Column(db.Float)
    created_at = db.Column(db.DateTime)   # start_time
    modified_at = db.Column(db.DateTime)  # end_time - null if session in progress
#    tariff = db.Column(db.Float)          # €/kWh
#    total_energy = db.Column(db.Float)    # kWh (end_value - start_value) - increasing during session
#    total_price = db.Column(db.Float)     # € (total_energy * tariff) - increasing during session
    energy_device_id = db.Column(db.String(100))

    # class constructor
    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.models.SessionModel')
        self.logger.debug('Initializing SessionModel without data')

    def set(self, data):
        for key in data:
            setattr(self, key, data.get(key))
        if (data.created_at == None):
            self.created_at = datetime.datetime.now()
        if (data.modified_at == None):
            self.modified_at = datetime.datetime.now()

    def save(self):
        session = Session()
        session.add(self)
        session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.modified_at = datetime.datetime.now()

        session = Session()
        session.commit()

    def delete(self):
        session = Session()
        session.delete(self)
        session.commit()

    @staticmethod
    def get_all_sessions():
        session = Session()
        return session.query.all()

    @staticmethod
    def get_one_session(id):
        session = Session()
        return session.query.get(id)

    @staticmethod
    def get_latest_rfid_session(device, rfid=None):
        session = Session()
        qry_latest_id = session.query(func.max(SessionModel.id)).filter(SessionModel.energy_device_id == device)
        if rfid is not None:
            qry_latest_id = qry_latest_id.filter(SessionModel.rfid == str(rfid))
        latest_session = session.query(SessionModel).filter(SessionModel.id == qry_latest_id).first()
        return latest_session

    def __repr(self):
        return '<id {}>'.format(self.id)

    def get_last_n_sessions_since(self, energy_device_id=None, since_ts=None, n=-1):
        session = Session()
        if ( n == -1 ):
            if ( since_ts == None ):
                if ( energy_device_id == None ):
                    return session.query(SessionModel) \
                        .order_by(SessionModel.created_at.desc()).all()
                else: # filter energy_device_id
                    return session.query(SessionModel) \
                        .filter(SessionModel.energy_device_id == energy_device_id) \
                        .order_by(SessionModel.created_at.desc()).all()
            else: # filter since_ts
                if ( energy_device_id == None ):
                    return session.query(SessionModel) \
                        .filter(SessionModel.created_at >= self.date_str_to_datetime(since_ts)) \
                        .order_by(SessionModel.created_at.desc()).all()
                else: # filter energy_device_id
                    return session.query(SessionModel) \
                        .filter(SessionModel.energy_device_id == energy_device_id) \
                        .filter(SessionModel.created_at >= self.date_str_to_datetime(since_ts)) \
                        .order_by(SessionModel.created_at.desc()).all()
        else: # limit n
            if ( since_ts == None ):
                if ( energy_device_id == None ):
                    return session.query(SessionModel) \
                        .order_by(SessionModel.created_at.desc()).limit(n).all()
                else: # filter energy_device_id
                    return session.query(SessionModel) \
                        .filter(SessionModel.energy_device_id == energy_device_id) \
                        .order_by(SessionModel.created_at.desc()).limit(n).all()
            else: # filter since_ts
                if ( energy_device_id == None ):
                    return session.query(SessionModel) \
                        .filter(SessionModel.created_at >= self.date_str_to_datetime(since_ts)) \
                        .order_by(SessionModel.created_at.desc()).limit(n).all()
                else: # filter energy_device_id
                    return session.query(SessionModel) \
                        .filter(SessionModel.energy_device_id == energy_device_id) \
                        .filter(SessionModel.created_at >= self.date_str_to_datetime(since_ts)) \
                        .order_by(SessionModel.created_at.desc()).limit(n).all()

    def date_str_to_datetime(self, date_time_str):
        return datetime.datetime.strptime(date_time_str, '%d/%m/%Y, %H:%M:%S')

    # convert into JSON:
    def to_json(self):
        return (
            json.dumps({
                "energy_device_id": str(self.energy_device_id),
                "created_at": str(self.created_at.strftime("%d/%m/%Y, %H:%M:%S")),
#                "start_time": str(self.start_time.strftime("%d/%m/%Y, %H:%M:%S")),
                "rfid": self.rfid,
                "start_value": str(self.start_value),
                "end_value": str(self.end_value),
#                "tariff": str(self.tariff),
#                "total_energy": str(self.total_energy),
#                "total_price": str(self.total_price),
                "modified_at": str(self.modified_at.strftime("%d/%m/%Y, %H:%M:%S"))
#                "end_time": str(self.end_time.strftime("%d/%m/%Y, %H:%M:%S"))
                }
            )
        )

    # convert into dict:
    def to_dict(self):
        return ( {
            "energy_device_id": str(self.energy_device_id),
            "created_at": str(self.created_at.strftime("%d/%m/%Y, %H:%M:%S")),
#            "start_time": str(self.start_time.strftime("%d/%m/%Y, %H:%M:%S")),
            "rfid": self.rfid,
            "start_value": str(self.start_value),
            "end_value": str(self.end_value),
#            "tariff": str(self.tariff),
#            "total_energy": str(self.total_energy),
#            "total_price": str(self.total_price),
            "modified_at": str(self.modified_at.strftime("%d/%m/%Y, %H:%M:%S"))
#            "end_time": str(self.end_time.strftime("%d/%m/%Y, %H:%M:%S"))
            }
        )

class SessionSchema(Schema):
    """
    Session Schema
    """
    id = fields.Int(dump_only=True)
    rfid = fields.Str(required=True)
    energy_device_id = fields.Str(required=True)
    start_value = fields.Float(dump_only=True)
    end_value = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)


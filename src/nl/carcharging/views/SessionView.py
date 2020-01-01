from flask import request, json, Response, Blueprint
from ..models.SessionModel import SessionModel, SessionSchema
#from ..models.SessionMeasureModel import SessionMeasureModel, SessionMeasureSchema
from ..services.EnergyUtil import EnergyUtil
from flask_apscheduler import APScheduler

scheduler = APScheduler()

session_api = Blueprint('session', __name__)
session_schema = SessionSchema()


@session_api.route('/', methods=['POST'])
def create(energy_util: EnergyUtil):
    """
    Create Session Function
    """
    req_data = request.get_json()
    data = session_schema.load(req_data)

    # Check if session is running or not for rfid
    existing_session = SessionModel.get_latest_rfid_session(data['rfid'])

    if existing_session is None:
        data['start_value'] = energy_util.getMeasurementValue()
        session = SessionModel(data)
        session.save()
        ser_data = session_schema.dump(session)
    else:
        existing_session.end_value = energy_util.getMeasurementValue()
        existing_session.save()
        ser_data = session_schema.dump(existing_session)

    # if error:
    #     return custom_response(error, 400)


    toggle_measurement_job(energy_util, ser_data, existing_session is None)

    return custom_response(ser_data, 201)


def toggle_measurement_job(energy_util: EnergyUtil, session_data, start):
    measure_job = "measuring"
    if start:
        scheduler.add_job(id=measure_job, func=lambda: save_measurement(energy_util, session_data["id"]),
                      trigger="interval", seconds=10)
    else:
        scheduler.remove_job(measure_job);


def save_measurement(energy_util: EnergyUtil, session_id):
    app = scheduler.app
    with app.app_context():
        data = {"session_id": session_id, "value": energy_util.getMeasurementValue()}
        session_measurement = SessionMeasureModel(data)
        session_measurement.save()
    print("value measured and saved")


def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )

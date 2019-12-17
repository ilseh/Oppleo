from flask import request, json, Response, Blueprint
from ..models.SessionModel import SessionModel, SessionSchema
from ..models.SessionMeasureModel import SessionMeasureModel, SessionMeasureSchema
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
    data['start_value'] = energy_util.getMeasurementValue()

    # if error:
    #     return custom_response(error, 400)

    session = SessionModel(data)
    session.save()

    ser_data = session_schema.dump(session)

    measure_job = "measuring"
    scheduler.add_job(id=measure_job, func=lambda: save_measurement(energy_util, ser_data["id"]),
                      trigger="interval", seconds=10)

    return custom_response(ser_data, 201)


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

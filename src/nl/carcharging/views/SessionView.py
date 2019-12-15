from flask import request, json, Response, Blueprint
from ..models.SessionModel import SessionModel, SessionSchema
from ..services.EnergyUtil import EnergyUtil


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

    return custom_response(ser_data, 201)

def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )

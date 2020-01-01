from flask import Flask, render_template, jsonify, Response
from flask_socketio import SocketIO
from config import app_config
from nl.carcharging.models import db
from nl.carcharging.views.SessionView import session_api as session_blueprint
from nl.carcharging.views.SessionView import scheduler
import os
from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.services.EnergyUtil import EnergyUtil




# app initiliazation
app = Flask(__name__)

app.config.from_object(app_config[os.getenv('CARCHARGING_ENV')])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = '(*^&uytwejkfh8tsefukhg23eioHJYseryg(*^5eyt123eiuyowish))!'

socketio = SocketIO(app)

app.register_blueprint(session_blueprint, url_prefix='/api/v1/sessions')

db.init_app(app)

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/usage")
def usage():
    return render_template("usage.html")

@app.route("/usage_data")
def usage_data():
    device_measurement = EnergyDeviceMeasureModel(  
        EnergyUtil().getDevMeasurementValue(energy_device_id="laadpaal_noord")        
    )
    qr = device_measurement.get_last_n_saved(energy_device_id="laadpaal_noord",n=100)
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())  

    return jsonify(qr_l)


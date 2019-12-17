from flask import Flask
from config import app_config
from nl.carcharging.models import db
from nl.carcharging.views.SessionView import session_api as session_blueprint
from nl.carcharging.views.SessionView import scheduler


def create_app(env_name):
    """
    Create app
    """

    # app initiliazation
    app = Flask(__name__)

    app.config.from_object(app_config[env_name])
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.register_blueprint(session_blueprint, url_prefix='/api/v1/sessions')

    db.init_app(app)

    scheduler.init_app(app)
    scheduler.start()

    @app.route('/', methods=['GET'])
    def index():
        """
        example endpoint
        """
        return 'Congratulations! Your first endpoint is workin'

    return app

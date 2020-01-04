import os
from nl.carcharging.services.EnergyUtil import EnergyUtil
from flask_injector import FlaskInjector
from src.app import create_app
import logging


logging.basicConfig(level=logging.DEBUG)


def configure(binder):
    binder.bind(
        EnergyUtil,
        to=EnergyUtil
    )


if __name__ == '__main__':
    env_name = os.getenv('FLASK_ENV')
    app = create_app(env_name)

    FlaskInjector(app=app, modules=[configure])

    # run app
    app.run()

import os

# import requests
from flask import Flask


def run_heater(test_config=None, *, ip: str = '127.0.0.1', port: int = 5003) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'secret_key'
    # run generator in thread -> app.config['generator']
    # app.config.from_mapping()
    if test_config is None:
        # app.config.from_pyfile('config.py', silent=True)
        app.config.from_object('config.Dev')
    else:  # pragma: no cover
        app.config.from_mapping(test_config)
    app.config['address'] = f'{ip}:{port}'
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # generator

    # routes
    @app.route('/')
    def index():
        return app.config['address']

    with app.app_context():
        from pisklak.heater.heater import ElectricHeater
        app.register_blueprint(ElectricHeater.mod)
        ElectricHeater.run()

    return app

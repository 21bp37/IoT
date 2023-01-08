import os
import threading

# import requests
from flask import Flask


def run_aggregator(test_config=None, *, ip: str = '127.0.0.1', port: int = None) -> Flask:
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
        from pisklak.aggregator.aggregator import Aggregator
        app.register_blueprint(Aggregator.mod)
        # Aggregator.register(app.config['address'])
        # reg_thread = threading.Thread(target=requests.get,
        # daemon=True, kwargs={'url': 'http://127.0.0.1:5001/register'})
        # reg_thread.start()
        # rejestracja agregatora na adres zarządczy autoamtycznie, żeby nie rejestrować agregatora ręcznie
        # żeby zarejestrować nowy agregator u zarządcy
        # można wysłać posta na odpowiedni interfejs zarządcy /register

        reg_thread = threading.Thread(target=Aggregator.register, daemon=True,
                                      kwargs={'address': '127.0.0.1:5001'})
        reg_thread.start()
        # Aggregator.register('127.0.0.1:5001')

    return app

import os
import threading

# import requests
from flask import Flask


def run_filter(test_config=None, *, ip: str = '127.0.0.1', port: int = None) -> Flask:
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
        from pisklak.filter.filter import Filter
        from pisklak.filter.filter_ver2 import Filter2
        app.register_blueprint(Filter.mod)
        app.register_blueprint(Filter2.mod)
        # Automatyczna rejestracja filtru, żeby nie rejestrować go ręcznie u zarządcy
        # aby zarejestrować ręcznie, należy podać zarządcy adres filtru oraz typ filter przez post /register
        reg_thread = threading.Thread(target=Filter.register, daemon=True,
                                      kwargs={'address': app.config['address']})
        reg_thread.start()
        reg_thread2 = threading.Thread(target=Filter2.register, daemon=True,
                                       kwargs={'address': app.config['address']})
        reg_thread2.start()
    return app

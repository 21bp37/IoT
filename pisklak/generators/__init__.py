import os
import queue
import uuid
from .z5.generator import run_publishers
from flask import Flask


def run_generator(test_config=None, *, ip: str = '127.0.0.1', port: int = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'secret_key'
    # run generator in thread -> app.config['generator']
    # app.config.from_mapping()
    if test_config is None:
        # app.config.from_pyfile('config.py', silent=True)
        app.config.from_object('config.Dev')
    else:  # pragma: no cover
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    # generator
    q: queue.Queue = queue.Queue()
    run_publishers(f'generator:{port}', str(uuid.uuid4()), './pisklak/generators/z5/config_single.toml', q,
                   address=f'{ip}:{port}')
    app.config['generator'] = q.get()

    # routes
    @app.route('/')
    def index():
        return str(app.config['generator'])

    with app.app_context():
        # import pisklak.manager.z1.views as file_handler
        # app.register_blueprint(file_handler.mod)
        import pisklak.generators.z5.views as config_handler
        app.register_blueprint(config_handler.mod)

        pass
    return app

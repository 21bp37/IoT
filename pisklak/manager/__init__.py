import os

from flask import Flask


def run_manager(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'secret_key'
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

    @app.route('/index')
    def index():
        return 'manager'

    with app.app_context():
        import pisklak.manager.z1.views as file_handler
        import pisklak.manager.z2.views as json_mqtt
        import pisklak.manager.z3.views as json_z3
        import pisklak.manager.z5.views as manager

        app.register_blueprint(file_handler.mod)
        app.register_blueprint(json_mqtt.mod)
        app.register_blueprint(json_z3.mod)
        app.register_blueprint(manager.mod)

    return app

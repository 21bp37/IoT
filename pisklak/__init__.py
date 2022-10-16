import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
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

    # @app.route('/')
    @app.route('/index')
    def index():
        return 'witanie'

    with app.app_context():
        import pisklak.z1.views

    return app

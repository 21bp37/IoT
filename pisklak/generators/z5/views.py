from flask import Blueprint, current_app, make_response, request

mod = Blueprint('flask_z5', __name__)


# print(app_socketio)


@mod.route('/pause', methods=['GET', 'POST'])
def pause():
    generator = current_app.config['generator']
    if request.method == 'POST':
        code = 500
        if generator.status == 'running':
            generator.paused = True
            code = 201
        return make_response(generator.status, code)
    return generator.status


@mod.route('/start', methods=['GET', 'POST'])
def start():
    generator = current_app.config['generator']
    if request.method == 'POST':
        code = 500
        if generator.status == 'paused':
            generator.paused = False
            code = 201
        return make_response(generator.status, code)
    return generator.status


@mod.route('/update', methods=['GET', 'POST'])
def update():
    generator = current_app.config['generator']
    if request.method == 'POST':
        try:
            generator.protocol = request.form['protocol']
            generator.interval = float(request.form['interval'])
            generator.data_source = request.form['data_source']
            generator.url = request.form['url']
            return make_response(generator.status, 201)
        except KeyError:
            return make_response('key error', 500)
    return generator.status

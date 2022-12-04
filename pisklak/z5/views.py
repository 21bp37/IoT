import logging
from .generator import run_publishers
from flask import Blueprint, request, render_template
from .. import app_socketio
import flask_socketio  # type: ignore
import threading
import uuid
import os

mod = Blueprint('flask_z5', __name__)

# print(app_socketio)

generator_apps = []


def run_generators() -> None:
    for i in range(2):
        """cfg = {
            'name': f'app{i}',
            'protocol': 'mqtt',
            'interval': 4,
            'data_source': './pisklak_clients/datasets/beach_weather.csv',
            'url': 'test.mosquitto.org',
            'uuid': uuid.uuid4()
        }"""
        """gen = {
            'config': {},
            'app': run_publishers(cfg)
        }"""
        thread = threading.Thread(target=run_publishers,
                                  args=(f'app_{i + 1}', str(uuid.uuid4()), './pisklak/z5/config_single.toml'))
        thread.daemon = True
        thread.start()
        thread.join()
        # gens.append(gen)


if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    run_generators()


@app_socketio.on('register', namespace='/')
def joined(message):
    # print(f'joined {message}')
    sid = message['uuid']
    flask_socketio.join_room(sid)
    logging.warning(f'tytka {message}')


@mod.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        data = dict(request.form)
        generator_apps.append(data)
        # flask_socketio.join_room(data['uuid'])
        """try:
            clients.append(data)
        except KeyError as e:
            logging.warning(e)"""
        return ''


@mod.route('/generators2', methods=['GET', 'POST'])
def generators():
    if request.method == 'POST':
        sid = request.form['uuid']
        gen = list(filter(lambda client: client['uuid'] == sid, generator_apps))[0]
        gen['protocol'] = request.form['protocol']
        gen['interval'] = request.form['interval']
        gen['data_source'] = request.form['source']
        gen['url'] = request.form['url']
        # gen['status'] = request.form['status']
        flask_socketio.emit('update', gen, room=sid, namespace='/')
        return render_template('manager2.html', client=gen)
    if request.method == 'GET' and request.args.get('id') is not None:
        try:
            selected = list(filter(lambda client: client['uuid'] == request.args.get('id'), generator_apps))
            return render_template('manager2.html', client=selected[0])
        except IndexError:
            return 'generator not found.'
    return render_template('generators2.html', clients=generator_apps)

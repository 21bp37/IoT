import logging

from flask import Blueprint, request, session, render_template
from .. import app_socketio
import flask_socketio  # type: ignore

mod = Blueprint('flask_socketio', __name__)
# print(app_socketio)

clients = []


@app_socketio.on('register', namespace='/')
def joined(message):
    # print(f'joined {message}')
    sid = request.sid  # noqa
    flask_socketio.join_room(sid)
    client_data = {'id': sid, 'room': session.get('room')}
    client_data.update(message)
    clients.append(client_data)
    logging.warning(message)


@app_socketio.on('disconnect', namespace='/')
@app_socketio.on_error('/')
def logout(e):
    logging.warning(e)
    try:
        sid = request.sid  # noqa
        filtered = list(filter(lambda client: client['id'] == sid, clients))
        clients.remove(filtered[0])
        logging.warning(f'removed client {sid}')
    except (IndexError, KeyError) as ex:
        logging.warning(ex)


@mod.route('/generators', methods=['GET', 'POST'])
def generators():
    if request.method == 'POST':
        sid = request.form['id']
        gen = list(filter(lambda client: client['id'] == sid, clients))[0]
        gen['protocol'] = request.form['protocol']
        gen['interval'] = request.form['interval']
        gen['data_source'] = request.form['source']
        gen['url'] = request.form['url']
        flask_socketio.emit('update', gen, room=sid, namespace='/')
        return render_template('manager.html', client=gen)
    if request.method == 'GET' and request.args.get('id') is not None:
        try:
            selected = list(filter(lambda client: client['id'] == request.args.get('id'), clients))
            return render_template('manager.html', client=selected[0])
        except IndexError:
            return 'generator not found.'
    return render_template('generators.html', clients=clients)

import requests
from flask import Blueprint, request, render_template

mod = Blueprint('flask_z5', __name__)

generator_apps = []


@mod.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = {
                'name': request.form['name'],
                'protocol': request.form['protocol'],
                'interval': request.form['interval'],
                'data_source': request.form['data_source'],
                'url': request.form['url'],
                'uuid': request.form['uuid'],
                'status': request.form['status'],
                'address': request.form['address'] if 'address' in request.form
                else f'{request.remote_addr}:{request.environ.get("REMOTE_PORT")}'
            }
            generator_apps.append(data)
        except KeyError:
            return 'missing config data'
    return str(generator_apps)


@mod.route('/generators', methods=['GET', 'POST'])
def generators():
    if request.method == 'POST':
        sid = request.form['uuid']
        gen = list(filter(lambda client: client['uuid'] == sid, generator_apps))[0]
        if 'uuid' not in request.form or not gen:
            return 'Niepoprawny generator'
        if 'update' in request.form:
            response = requests.post(
                f'http://{gen["address"]}/update',
                data={
                    'protocol': request.form['protocol'],
                    'interval': request.form['interval'],
                    'data_source': request.form['source'],
                    'url': request.form['url']
                }
            )
            # if success:
            if response.status_code == 201:
                gen['protocol'] = request.form['protocol']
                gen['interval'] = request.form['interval']
                gen['data_source'] = request.form['source']
                gen['url'] = request.form['url']
                # gen['status'] = request.form['status']

                return render_template('manager2.html', client=gen)
            return str(response.status_code)
        # Zarządca - wstrzymanie generatora
        if 'pause' in request.form:
            response = requests.post(f'http://{gen["address"]}/pause')
            if response.status_code == 201:
                gen['status'] = 'paused'
                return render_template('manager2.html', client=gen)
            return 'Generator jest już zatrzymany.'

        # Zarządca - Wznowienie generatora
        if 'start' in request.form:
            response = requests.post(f'http://{gen["address"]}/start')
            if response.status_code == 201:
                gen['status'] = 'running'
                return render_template('manager2.html', client=gen)
            return 'Generator już działa.'

        return render_template('generators2.html', clients=generator_apps)
    if request.method == 'GET' and request.args.get('id') is not None:
        try:
            selected = list(filter(lambda client: client['uuid'] == request.args.get('id'), generator_apps))
            return render_template('manager2.html', client=selected[0])
        except IndexError:
            return 'generator not found'
    return render_template('generators2.html', clients=generator_apps)

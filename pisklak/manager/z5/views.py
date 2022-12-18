import requests
from flask import Blueprint, request, render_template

mod = Blueprint('flask_z5', __name__)
aggregators = []
generator_apps = []
gen2 = []


@mod.route('/test', methods=['GET', 'POST'])
def test():
    return str(aggregators)


@mod.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            if 'type' not in request.form or request.form['type'] == 'generator':
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
                gen2.append(data)
                # generator_apps.append(data)
                generator_apps.append(request.form['address'])
            elif request.form['type'] == 'aggregator':
                data = {
                    'address': request.form['address']
                }
                if data in aggregators:
                    return
                aggregators.append(data)
                aggregator_config = {
                    'interval': 3600,
                    'destination': 'test.mosquitto.org',
                    'protocol': 'mqtt'
                }
                requests.post(f"http://{data['address']}/configure", data=aggregator_config)
        except KeyError:
            return 'missing config data'
    return str(generator_apps)


@mod.route('/generators', methods=['GET', 'POST'])
def generators():
    if request.method == 'POST':
        sid = request.form['uuid']
        gen = list(filter(lambda client: client['uuid'] == sid, gen2))[0]
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

        return render_template('generators2.html', clients=gen2)
    if request.method == 'GET' and request.args.get('id') is not None:
        try:
            selected = list(filter(lambda client: client['uuid'] == request.args.get('id'), gen2))
            return render_template('manager2.html', client=selected[0])
        except IndexError:
            return 'generator not found'
    return render_template('generators2.html', clients=gen2)


@mod.route('/generators2', methods=['GET', 'POST'])
def generators2():
    if request.method == 'POST':
        gen_address = list(filter(lambda client: client == request.args.get('ip'), generator_apps))[0]
        if 'ip' not in request.form or not gen_address:
            return 'Niepoprawny generator'
        if 'update' in request.form:
            response = requests.post(
                f'http://{gen_address}/update',
                data={
                    'protocol': request.form['protocol'],
                    'interval': request.form['interval'],
                    'data_source': request.form['source'],
                    'url': request.form['url']
                }
            )
            # if success:
            if response.status_code == 201:
                gen_status = requests.get(f'http://{gen_address}/status')
                data = dict(gen_status.json())
                return render_template('manager.html', client=data)
            return str(response.status_code)
        # Zarządca - wstrzymanie generatora

        if 'pause' in request.form:
            response = requests.post(f'http://{gen_address}/pause')
            if response.status_code == 201:
                gen_status = requests.get(f'http://{gen_address}/status')
                data = dict(gen_status.json())
                return render_template('manager.html', client=data)
            return 'Generator jest już zatrzymany.'

        # Zarządca - Wznowienie generatora
        if 'start' in request.form:
            response = requests.post(f'http://{gen_address}/start')
            if response.status_code == 201:
                gen_status = requests.get(f'http://{gen_address}/status')
                data = dict(gen_status.json())
                return render_template('manager.html', client=data)
            return 'Generator już działa.'

        return render_template('generators.html', clients=generator_apps)
    if request.method == 'GET' and request.args.get('ip') is not None:
        try:
            gen_address = list(filter(lambda client: client == request.args.get('ip'), generator_apps))[0]
            response = requests.get(f'http://{gen_address}/status')
            return render_template('manager.html', client=dict(response.json()))
        except IndexError:
            return 'generator not found'
    data = []
    for address in generator_apps:
        response = requests.get(f'http://{address}/status')
        data.append(dict(response.json()))
    return render_template('generators.html', clients=data)

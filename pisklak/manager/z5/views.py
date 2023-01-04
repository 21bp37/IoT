import requests
from flask import Blueprint, request, render_template

mod = Blueprint('flask_z5', __name__)
aggregators = []
generator_apps = []


# gen2 = []


@mod.route('/test', methods=['GET', 'POST'])
def test():
    return str(aggregators)


@mod.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            if 'type' not in request.form or request.form['type'] == 'generator':
                """data = {
                    'address': request.form['address'] if 'address' in request.form
                    else f'{request.remote_addr}:{request.environ.get("REMOTE_PORT")}'
                }"""
                # generator_apps.append(data)
                generator_apps.append(str(request.form['address']))
            elif request.form['type'] == 'aggregator':
                data = {
                    'address': request.form['address']
                }
                if data in aggregators:
                    return
                aggregators.append(data)
                aggregator_config = {
                    'interval': 8,
                    'destination': 'test.mosquitto.org',
                    'protocol': 'mqtt',
                    'running': True
                }
                requests.post(f"http://{data['address']}/configure", data=aggregator_config)
                # zmiana configu generatorow gdy pojawi sie agregator:
                # (zeby nie zmieniac recznie na potrzeby zadania)
                for gen_cl in generator_apps:
                    gen_address = gen_cl
                    requests.post(
                        f'http://{gen_address}/update',
                        data={
                            'protocol': 'http',
                            'url': f"http://{request.form['address']}/send"
                        }
                    )
        except KeyError:
            return 'missing config data'
    return str(generator_apps)


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


@mod.route('/aggregators', methods=['GET', 'POST'])
def aggregators_list():
    aggregator_cfgs = []

    for aggregator in aggregators:
        conf = dict(requests.post(f"http://{aggregator['address']}/status").json())
        conf['address'] = aggregator['address']
        aggregator_cfgs.append(conf)
    # return aggregator_cfgs
    if request.method == 'POST':
        aggregator_address = list(filter(lambda client: client['address'] == request.args.get('ip'),
                                         aggregators))[0]['address']
        if 'ip' not in request.form or not aggregator_address:
            return 'Niepoprawny generator'
        if 'update' in request.form:
            response = requests.post(
                f'http://{aggregator_address}/configure',
                data={
                    'protocol': request.form['protocol'],
                    'interval': request.form['interval'],
                    'destination': request.form['destination']
                }
            )
            # if success:
            if response.status_code == 201:
                aggregator_status = requests.get(f'http://{aggregator_address}/status')
                data = dict(aggregator_status.json())
                data['address'] = aggregator_address
                return render_template('aggregator_manager.html', client=data)
            return str(response.status_code)
        # Zarządca - wstrzymanie agregatora

        if 'pause' in request.form:
            response = requests.post(f'http://{aggregator_address}/stop')
            if response.status_code == 201:
                gen_status = requests.get(f'http://{aggregator_address}/status')
                data = dict(gen_status.json())
                data['address'] = aggregator_address
                return render_template('aggregator_manager.html', client=data)
            return 'Generator jest już zatrzymany.'

        # Zarządca - Wznowienie agregatora
        if 'start' in request.form:
            response = requests.post(f'http://{aggregator_address}/start')
            if response.status_code == 201:
                gen_status = requests.get(f'http://{aggregator_address}/status')
                data = dict(gen_status.json())
                data['address'] = aggregator_address
                return render_template('aggregator_manager.html', client=data)
            return 'Generator już działa.'

        return render_template('aggregators.html', clients=aggregator_cfgs)
    if request.method == 'GET' and request.args.get('ip') is not None:
        try:
            gen_address = list(filter(lambda client: client['address'] == request.args.get('ip'),
                                      aggregators))[0]['address']
            response = requests.get(f'http://{gen_address}/status')
            data = dict(response.json())
            data['address'] = gen_address
            return render_template('aggregator_manager.html', client=data)
        except IndexError:
            return 'generator not found'
    return render_template('aggregators.html', clients=aggregator_cfgs)

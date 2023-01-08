import json

import requests
from flask import Blueprint, request, render_template, make_response

mod = Blueprint('flask_z5', __name__)
aggregators: list[dict] = []
generator_apps: list[str] = []
filters: list[dict] = []


# gen2 = []


@mod.route('/test', methods=['GET', 'POST'])
def test():
    return str(aggregators)


@mod.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            if 'type' not in request.form or request.form['type'] == 'generator':
                generator_apps.append(str(request.form['address']))
            elif request.form['type'] == 'aggregator':
                data = {
                    'address': request.form['address']
                }
                if data in aggregators:
                    return make_response('agregat jest już zarejestrowany', 500)
                aggregators.append(data)
                # wysyłanie configu przy rejestrajci agregatora
                # zrobione na potrzebę zadania, żeby nie wysyłać ręcznie configu przez forma podając go zarządcy
                # żeby sprawniej pokazać działanie zadania.
                # zarządca wysyła posta na opdowiedni intrefejs agregatora z zadaną konfiguracją.
                # aby zmienić ręcznie config można wysłać posta na interfejs zarządcy:
                # ip_zarządcy/aggregators z parametrem update oraz zadaną konfiguracją.
                # wtedy zarządca wysyła post z parametrami na interfejs agregatora.
                # Agregator przy uruchamianiu nie ma swojej konfiguracji, dostaję ją dopiero
                # po otrzymaniu przez zarządcę.
                # przekazywanie conifgu w każdej z tych sytuacji pochodzi od zarządcy:
                # Zarządca  -(post z configiem)-> agregator
                if 'config' in request.form:
                    aggregator_config = request.form['config']
                else:
                    aggregator_config = {
                        'interval': 8,
                        'destination': 'http://127.0.0.1:5002/send2',
                        'protocol': 'http',
                        'running': True
                    }
                requests.post(f"http://{data['address']}/configure", data=aggregator_config)
            elif request.form['type'] == 'filter':
                data = {
                    'address': request.form['address']
                }
                if data in filters:
                    return make_response('filtr jest już zarejestrowany', 500)
                filters.append(data)
                ####
                """
                Zrobione na potrzeby debugowania kodu: wysyłanie configu przy rejestacji
                (post zarejestruj filtr, dane: adres, config)-> zarządca -(post config)-> filtr)
                 przesłania forma ręcznie
                """
                if 'config' in request.form:
                    filter_config = request.form['config']
                else:
                    filter_config = {
                        'destination': 'test.mosquitto.org',
                        'protocol': 'mqtt',
                        'running': True,
                        'filters': json.dumps(['wind_direction', 'wind_speed', 'wind_chill'])
                    }
                #######
                requests.post(f"http://{data['address']}/configure", data=filter_config)
                """druga implementacja filtru (z podanym adresem źródła)"""
                filter_config = [
                    {
                        'source': '127.0.0.1:5001',
                        'destination': 'test.mosquitto.org',
                        'protocol': 'mqtt',
                        'filters': ['wind_direction', 'wind_speed', 'wind_chill']
                    },
                    {
                        'source': '127.0.0.1:5009',
                        'destination': 'test.mosquitto.org',
                        'protocol': 'mqtt',
                        'filters': ['wind_direction', 'wind_speed', 'wind_chill']
                    }
                ]
                requests.post(f"http://{data['address']}/configure2", json=filter_config)
        except KeyError:
            return 'missing config data'
    return str(filters)


@mod.route('/update_filter', methods=['GET', 'POST'])
def update_filter():
    """Wysłanie do zarządcy nowego configu dla wskazanego filtru jeżeli byłobyto potrzebne.
    zarządca -> filtr"""
    if request.method == 'POST':
        address = request.form['address']
        if address in filters:
            filter_config = request.form['config']
            requests.post(f"http://{address}/configure", data=filter_config)
    return 'config'


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

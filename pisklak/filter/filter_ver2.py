import json
import logging

from flask import Blueprint, request, make_response, Response, current_app
import datetime
import requests
import paho.mqtt.client as mqtt  # type: ignore


class Filter2:
    mod: Blueprint = Blueprint('filter2', __name__)
    # time = time
    time: datetime.datetime | None = datetime.datetime.now()
    configs: list[dict] = []
    """config: dict = {
        'source': str,
        'destination': str,
        'protocol': str,
        'running': True,  # przy tworzeniu, ustawienie działania na true.
        # można domyślnie ustawić na False i wtedy uruchomienie nastąpi po otrzymaniu posta od zarządcy
        'filter': list  # Pola po których będą filtrowane dane.
        # po podaniu pola/pól, będą jedynie przesyłane dalej wybrane pola.
    }"""

    @staticmethod
    @mod.route('/status2', methods=['GET', 'POST'])
    def status():
        """Metoda zrobiona na potrzeby debugowania kodu"""
        return Filter2.configs

    @staticmethod
    @mod.route('/register2', methods=['GET', 'POST'])
    def route_register():
        """metoda utowrzona na potrzeby debugowania kodu"""
        if request.method == 'POST':
            try:
                Filter2.register(request.form['address'])
            except KeyError as e:
                logging.warning(e)
        code = Filter2.register(current_app.config['address'])
        if code == 201 or code == 200:
            return 'registered'
        return f'cannot register: {code}'

    @staticmethod
    def register(address: str) -> int:
        """metoda utowrzona na potrzeby debugowania kodu"""
        manager = 'http://127.0.0.1:5000/register'
        data = {
            'address': address,
            'type': 'filter'
        }
        response = requests.post(manager, data=data)
        return response.status_code

    @classmethod
    def send_data(cls, data, source) -> bool:
        config = list(filter(lambda cfg: cfg['source'] == source, cls.configs))[0]
        if config['protocol'] == 'mqtt':
            client = mqtt.Client('filter2137')
            client.connect(config['destination'], 1883)
            client.loop_start()
            if client is not None:
                logging.warning(
                    f'mqtt: Filter2: published topic data {data}\n')
                client.publish('filter2137', json.dumps(data))
            client.disconnect()
        if config['protocol'] == 'http':
            try:
                logging.warning(
                    f'http: Filter2: published topic data {data}\n')
                requests.post(f'{config["destination"]}', json=data)
            except (requests.exceptions.InvalidURL, requests.exceptions.RequestException) as e:
                logging.warning(f'http: filter exception: {e}\n')
        return True

    @classmethod
    def update_config(cls, *, source: str, destination: str, protocol: str, filters: list | str) -> bool:
        try:
            config = {
                'source': str(source),
                'destination': str(destination),
                'protocol': str(protocol),
                'filter': list
            }
            if not isinstance(filters, list):
                config['filter'] = json.loads(filters)
            else:
                config['filter'] = list(filters)
            cls.configs.append(config)
            return True
        except ValueError:
            return False

    @staticmethod
    @mod.route('/configure2', methods=['GET', 'POST'])
    def configure() -> Response:
        if request.method == 'POST':
            content = json.loads(json.dumps(request.json))
            logging.warning(f'\n\n\n\n{content}\n\n\n')
            try:
                for config in content:
                    logging.warning(f'\n\n\n\n{config}\n\n\n')
                    Filter2.update_config(**dict(config))
            except KeyError as e:
                return make_response(e, 500)
        return make_response(Filter2.configs, 201)

    @staticmethod
    @mod.route('/send2', methods=['GET', 'POST'])
    def filter_route() -> Response:
        """Metoda odpowiedzialna za odbieranie danych ze źródła/agregatu"""
        if request.method == 'POST':
            content = request.json
            if not content:
                return make_response('No json part', 422)
            if content == '':
                return make_response('Json not found', 400)
            json_data = json.loads(json.dumps(content))

            source = str(json_data['address'])
            # Przefiltrowanie danych na podstawie zadanej konfiguracji:
            filtered_data = Filter2.filter_data(json_data, source)
            logging.warning(f'Filtr2: przefiltrowane dane: {filtered_data}')
            # Wysłanie przefiltrowanych danych:
            Filter2.send_data(filtered_data, source)
            return make_response(filtered_data)
        return make_response('ok')

    @classmethod
    def filter_data(cls, data: dict, source) -> dict:
        config = list(filter(lambda cfg: cfg['source'] == source, cls.configs))[0]
        if not config:
            return data
        if not config['filter']:
            return data
        new_data = {}
        for key, field in data.items():
            if key in config['filter']:
                new_data[key] = field
        return new_data

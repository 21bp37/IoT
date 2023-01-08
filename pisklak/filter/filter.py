import json
import logging

from flask import Blueprint, request, make_response, Response, current_app
import datetime
import requests
import paho.mqtt.client as mqtt


class Filter:
    mod: Blueprint = Blueprint('filter', __name__)
    # time = time
    time: datetime.datetime | None = datetime.datetime.now()
    config: dict = {
        'destination': str,
        'protocol': str,
        'running': True,  # przy tworzeniu, ustawienie działania na true.
        # można domyślnie ustawić na False i wtedy uruchomienie nastąpi po otrzymaniu posta od zarządcy
        'filter': list  # Pola po których będą filtrowane dane.
        # po podaniu pola/pól, będą jedynie przesyłane dalej wybrane pola.
    }

    @classmethod
    def is_running(cls):
        return cls.config['running']

    @staticmethod
    @mod.route('/status', methods=['GET', 'POST'])
    def status():
        """Metoda zrobiona na potrzeby debugowania kodu"""
        return Filter.config

    @staticmethod
    @mod.route('/start', methods=['GET', 'POST'])
    def start():
        """Wznowienie filtra - filtr przy otrzymaniu danych przesyła je dalej"""
        if Filter.is_running():
            return make_response('Filtr juz dziala', 500)
        Filter.config['running'] = True
        return make_response(str(Filter.is_running()), 201)

    @staticmethod
    @mod.route('/stop', methods=['GET', 'POST'])
    def stop():
        """Zatrzymanie filtra (filter nie wysyła dalej danych,
        co zostaje wysłane do filtra zostaje utracone)"""
        if not Filter.is_running():
            return make_response('Filtr juz jest zatrzymany', 500)
        Filter.config['running'] = False
        return make_response(str(Filter.is_running()), 201)

    @staticmethod
    @mod.route('/register', methods=['GET', 'POST'])
    def route_register():
        """metoda utowrzona na potrzeby debugowania kodu"""
        if request.method == 'POST':
            try:
                Filter.register(request.form['address'])
            except KeyError as e:
                logging.warning(e)
        code = Filter.register(current_app.config['address'])
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
    def send_data(cls, data) -> bool:
        if not cls.is_running():
            logging.warning(
                f'Filter: Filter is not running {data}\n')
            return False
        if cls.config['protocol'] == 'mqtt':
            client = mqtt.Client('filter2137')
            client.connect(cls.config['destination'], 1883)
            client.loop_start()
            if client is not None:
                logging.warning(
                    f'mqtt: Filter: published topic data {data}\n')
                client.publish('filter2137', json.dumps(data))
            client.disconnect()
        if cls.config['protocol'] == 'http':
            try:
                logging.warning(
                    f'http: Filter: published topic data {data}\n')
                requests.post(f'{cls.config["destination"]}', json=data)
            except (requests.exceptions.InvalidURL, requests.exceptions.RequestException) as e:
                logging.warning(f'http: filter exception: {e}\n')
        return True

    @classmethod
    def update_config(cls, *, destination: str, protocol: str, running: bool, filters: list | str) -> bool:
        # try except..
        try:
            cls.config['destination'] = str(destination)
            cls.config['protocol'] = str(protocol)
            cls.config['running'] = running
            if not isinstance(filters, list):
                cls.config['filter'] = json.loads(filters)
            else:
                cls.config['filter'] = filters
            return True
        except ValueError:
            return False

    @staticmethod
    @mod.route('/configure', methods=['GET', 'POST'])
    def configure() -> Response:
        if request.method == 'POST':
            content = dict(request.form)
            try:
                Filter.update_config(**content)
            except KeyError as e:
                return make_response(e, 500)
        return make_response(Filter.config, 201)

    @staticmethod
    @mod.route('/send', methods=['GET', 'POST'])
    def filter_route() -> Response:
        """Metoda odpowiedzialna za odbieranie danych ze źródła/agregatu"""
        if request.method == 'POST':
            content = request.json
            if not content:
                return make_response('No json part', 422)
            if content == '':
                return make_response('Json  not found', 400)
            json_data = json.loads(json.dumps(content))
            # Przefiltrowanie danych na podstawie zadanej konfiguracji:
            filtered_data = Filter.filter_data(json_data)
            logging.warning(f'Filtr: przefiltrowane dane: {filtered_data}')
            # Wysłanie przefiltrowanych danych:
            Filter.send_data(filtered_data)
            return make_response(filtered_data)
        return make_response('ok')

    @classmethod
    def filter_data(cls, data: dict) -> dict:
        if not cls.config['filter']:
            return data
        new_data = {}
        for key, field in data.items():
            if key in cls.config['filter']:
                new_data[key] = field
        return new_data

import json
import logging

from flask import Blueprint, request, make_response, Response, current_app
from collections import Counter
import datetime
import requests
import numpy as np
import paho.mqtt.client as mqtt


class Aggregator:
    mod: Blueprint = Blueprint('data_aggregation', __name__)
    data: list[dict] = []
    # time = time
    time: datetime.datetime | None = datetime.datetime.now()
    config: dict = {
        'interval': int,
        'destination': str,
        'protocol': str,
        'running': True
    }

    @classmethod
    def is_running(cls):
        return cls.config['running']

    @staticmethod
    @mod.route('/status', methods=['GET', 'POST'])
    def status():
        return Aggregator.config

    @staticmethod
    @mod.route('/start', methods=['GET', 'POST'])
    def start():
        if Aggregator.is_running():
            return make_response('Agregator juz dziala', 500)
        Aggregator.config['running'] = True
        return make_response(str(Aggregator.is_running()), 201)

    @staticmethod
    @mod.route('/stop', methods=['GET', 'POST'])
    def stop():
        if not Aggregator.is_running():
            return make_response('Agregator juz jest zatrzymany', 500)
        Aggregator.config['running'] = False
        return make_response(str(Aggregator.is_running()), 201)

    @staticmethod
    @mod.route('/register', methods=['GET', 'POST'])
    def call_register():
        if request.method == 'POST':
            try:
                Aggregator.register(request.form['address'])
            except KeyError as e:
                logging.warning(e)
        Aggregator.register(current_app.config['address'])
        return 'registered'

    @staticmethod
    def register(address: str) -> None:
        manager = 'http://127.0.0.1:5000/register'
        data = {
            'address': address,
            'type': 'aggregator'
        }
        requests.post(manager, data=data)

    @staticmethod
    def compress_data(data: list[dict]) -> dict:
        """
        # test
        with open('pisklak\\aggregator\\test.csv', 'r') as f:
            a = [{k: v for k, v in row.items()}
                 for row in csv.DictReader(f, skipinitialspace=True, delimiter=';')]
        data = a
        """
        compressed_data = {}
        try:
            for key in data[0].keys():
                try:
                    compressed_data[key] = np.mean([float(d[key]) for d in data], axis=0)
                except (TypeError, ValueError):
                    collected = Counter([d[key] for d in data])
                    compressed_data[key] = collected.most_common()[0][0]
            return compressed_data
        except IndexError:
            return {}

    @classmethod
    def send_data(cls) -> bool:
        data = cls.compress_data(cls.data)
        if cls.config['protocol'] == 'mqtt':
            client = mqtt.Client('aggregator2137')
            client.connect(cls.config['destination'], 1883)
            client.loop_start()
            if client is not None:
                logging.warning(
                    f'mqtt: aggregator: published topic data {data}\n')
                # print(json_data)
                client.publish('aggregator2137', json.dumps(data))
            client.disconnect()
        if cls.config['protocol'] == 'http':
            try:
                logging.warning(
                    f'http: aggregator: published topic data {data}\n')
                requests.post(f'{cls.config["destination"]}', json=data)
            except (requests.exceptions.InvalidURL, requests.exceptions.RequestException) as e:
                logging.warning(f'http: aggregator: {e}\n')
        return True

    @classmethod
    def check_aggregation(cls, timestamp: datetime.datetime) -> str:
        if abs((cls.time - timestamp).total_seconds()) <= float(cls.config['interval']):
            return f"{abs((cls.time - timestamp).total_seconds())}, {cls.config['interval']}"
        if Aggregator.is_running() and Aggregator.send_data():
            cls.time = datetime.datetime.now()
            cls.data = []
        return str(cls.data)

    @classmethod
    def update_config(cls, *, interval: float, destination: str, protocol: str) -> bool:
        # try except..
        cls.config['interval'] = float(interval)
        cls.config['destination'] = str(destination)
        cls.config['protocol'] = str(protocol)
        return True

    @staticmethod
    @mod.route('/configure', methods=['GET', 'POST'])
    def configure() -> Response:
        if request.method == 'POST':
            content = dict(request.form)
            try:
                Aggregator.update_config(**content)
                Aggregator.config['running'] = True
            except KeyError as e:
                return make_response(e, 500)
        return make_response(Aggregator.config, 201)

    @staticmethod
    @mod.route('/send', methods=['GET', 'POST'])
    def aggregation() -> Response:
        if request.method == 'POST':
            content = request.json
            if not content:
                return make_response('No json part', 422)
            if content == '':
                return make_response('Json  not found', 400)

            # data received
            json_data = json.loads(content)
            Aggregator.data.append(json_data)
            # time difference calculation
            """try:
                timestamp = datetime.datetime.timestamp(dict(json_data)['time'])
            except KeyError:
                timestamp = datetime.datetime.now()"""
            timestamp = datetime.datetime.now()
            if Aggregator.time is None:
                Aggregator.time = timestamp
            if Aggregator.config['running']:
                Aggregator.check_aggregation(timestamp)

            # if time difference = 1h send else append (timestamp-time) = 1h
            return make_response(json_data)
        return make_response('ok')

    @staticmethod
    @mod.route('/test', methods=['GET', 'POST'])
    def aggregation2() -> Response:
        collected_data = Aggregator.data
        compressed_data = Aggregator.compress_data(collected_data)
        return make_response(compressed_data)

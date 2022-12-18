import json
import logging

from flask import Blueprint, request, make_response, Response, current_app
from collections import Counter
import datetime
import requests
import numpy as np


class Aggregator:
    mod: Blueprint = Blueprint('data_aggregation', __name__)
    data: list[dict] = []
    # time = time
    time: datetime.datetime | None = None
    config: dict = {
        'interval': int,
        'destination': str,
        'protocol': str
    }

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
        for key in data[0].keys():
            try:
                compressed_data[key] = np.mean([float(d[key]) for d in data], axis=0)
            except (TypeError, ValueError):
                collected = Counter([d[key] for d in data])
                compressed_data[key] = collected.most_common()[0][0]
        return compressed_data

    @classmethod
    def send_data(cls) -> bool:
        data = cls.compress_data(cls.data)
        # send data
        return True

    @classmethod
    def check_aggregation(cls, timestamp: datetime.datetime) -> list:
        if abs((Aggregator.time - timestamp).total_seconds() <= Aggregator.config['interval']):
            return cls.data
        if Aggregator.send_data():
            cls.data = []
        return cls.data

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
            except KeyError as e:
                return make_response(e, 500)
        return make_response(str(Aggregator.config), 200)

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
            # todo
            try:
                timestamp = datetime.datetime.timestamp(dict(json_data)['time'])
            except KeyError:
                timestamp = datetime.datetime.now()
            if Aggregator.time is None:
                Aggregator.time = timestamp
            Aggregator.check_aggregation(timestamp)

            # if time difference = 1h send else append (timestamp-time) = 1h
            return make_response(json_data)
        return make_response('ok')

    @staticmethod
    @mod.route('/test', methods=['GET', 'POST'])
    def aggregation2() -> Response:
        collected_data = Aggregator.data
        compressed_data = Aggregator.compress_data(collected_data)
        return make_response(str(compressed_data))

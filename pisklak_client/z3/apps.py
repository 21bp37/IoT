from pathlib import Path
from urllib.parse import urlparse
import urllib.request
import paho.mqtt.client as mqtt
import time
import json
import requests
import csv
import toml


def load_config(conf_path: str | Path = 'config.toml') -> dict:
    data = toml.load(conf_path)
    return dict(data)


class Publisher:
    def __init__(self, data_source: str | Path = None, url: str = 'test.mosquitto.org', protocol: str = 'mqtt',
                 interval: float = 1, delim: str = ';', *, app_name: str = 'app'):
        self.data_source = data_source
        self.source_name = 'test_name'
        self.url = url
        if not protocol.lower() in ('http', 'mqtt'):
            raise ValueError(f'Unspported protocol: {url}')
        self.protocol = protocol.lower()
        self.interval = interval
        self.delim = delim
        self.app_name = app_name

    def __start(self, reader: csv.DictReader) -> None:
        if self.protocol == 'http':
            self.publish_http(dataset=reader)
            return
        if self.protocol == 'mqtt':
            self.publish_mqtt(dataset=reader)
            return

    def start(self, path: str | Path = None) -> None:
        path = self.data_source if not path else path
        if urlparse(str(path)).scheme in ('http', 'https'):
            dataset = urllib.request.urlopen(path).read()
            reader = csv.DictReader(dataset, delimiter=self.delim)
            self.__start(reader)
            return
        try:
            with open(path, 'r', newline='') as dataset:
                reader = csv.DictReader(dataset, delimiter=self.delim)
                self.__start(reader)
        except FileNotFoundError:
            print(f'file not found, skipping {self.data_source}')
        return

    def publish_mqtt(self, dataset: csv.DictReader, username: str = 'pisklak123') -> None:
        client = mqtt.Client(username)
        client.connect(self.url, 1883)
        client.loop_start()
        for data_sample in dataset:
            json_data = json.dumps(data_sample, indent=4)
            print(f'Mqtt: {self.app_name}:')
            # print(json_data)
            time.sleep(self.interval)
            client.publish(self.source_name, json_data)
        return

    def publish_http(self, dataset: csv.DictReader) -> None:
        for data_sample in dataset:
            json_data = json.dumps(data_sample, indent=4)
            time.sleep(self.interval)
            print(f'http {self.app_name}')
            requests.post(f'{self.url}', json=json_data)
        return


def subscriber(broker: str = 'test.mosquitto.org') -> None:
    def on_connect(client, _userdata, _flags, rc):
        client.subscribe('pisklak_ram')
        print(f"Connection returned result: {mqtt.connack_string(rc)}")

    def on_message(_client, _userdata, msg) -> None:
        # print(f'{msg.topic}: {msg.payload.decode()}')
        # print(str(msg.payload.decode()))
        json_data = json.loads(json.dumps(msg.payload.decode()))
        print(json_data)
        res = requests.post('http://127.0.0.1:5000/z2', json=json_data)
        print('---')
        print(f'Received: {res.text}')
        # post request

    mqttc = mqtt.Client('pisklak321')
    mqttc.connect(broker, 1883)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.loop_forever()


if __name__ == '__main__':
    from threading import Thread

    config = load_config()
    threads = []
    publishers = []
    for app_config in config['app'].items():
        publisher_app = Publisher(app_name=app_config[0], **app_config[1])
        publishers.append(publisher_app)
        thread = Thread(target=publisher_app.start)
        thread.daemon = True
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

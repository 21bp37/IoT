import csv
import json
import logging
import socket
import threading
import time
import urllib.request
from pathlib import Path
from threading import Thread, current_thread
from urllib.parse import urlparse

import paho.mqtt.client as mqtt  # type: ignore
import requests  # type: ignore
import toml  # type: ignore
import socketio  # type: ignore


def load_config(conf_path: str | Path = 'config.toml') -> dict:
    data = toml.load(conf_path)
    return dict(data)


class Publisher:
    def __init__(self, data_source: str | Path | None = None, url: str = 'test.mosquitto.org', protocol: str = 'mqtt',
                 interval: float = 1, delim: str = ';', *, app_name: str = 'app', uuid: str = '2137'):
        self.paused = False
        self.stop = False
        self.data_source: str | Path = data_source
        self.source_name: str = Path(data_source).stem
        self.url: str = url
        if not protocol.lower() in ('http', 'mqtt'):
            raise ValueError(f'Unsupported protocol: {url}')
        self.protocol: str = protocol.lower()
        self.interval: float = interval
        self.delim: str = delim
        self.app_name: str = app_name
        self.uuid = uuid
        # SocketIO
        self.sio = socketio.Client()
        self.listener = Thread(target=self.setup)
        self.listener.daemon = True
        self.listener.start()
        # self.listener.join()

    @property
    def status(self) -> str:
        return 'paused' if self.paused else 'running'

    def register_app(self):
        data = {
            'name': self.app_name,
            'protocol': self.protocol,
            'interval': self.interval,
            'data_source': self.data_source,
            'url': self.url,
            'uuid': self.uuid,
            'status': self.status
        }
        requests.post('http://localhost:5000/register', data=data)
        # logging.warning(response.content)

    def __start(self, reader: csv.DictReader) -> None:
        self.publish_any(dataset=reader)
        """if self.protocol == 'http':
            self.publish_http(dataset=reader)
            return
        if self.protocol == 'mqtt':
            self.publish_mqtt(dataset=reader)
            return"""

    def start(self, path: str | Path | None = None) -> None:
        path = self.data_source if not path else path
        if urlparse(str(path)).scheme in ('http', 'https'):
            dataset = urllib.request.urlopen(str(path)).read()
            reader = csv.DictReader(dataset, delimiter=self.delim)
            self.__start(reader)
            return
        try:
            with open(path, 'r', newline='') as dataset:
                reader = csv.DictReader(dataset, delimiter=self.delim)
                self.__start(reader)
        except FileNotFoundError:
            logging.info(f'file {path} not found, skipping {self.data_source}\n')
        return

    def connect_mqtt(self) -> mqtt.Client | None:
        try:
            client = mqtt.Client(self.app_name)
            client.connect(self.url, 1883)
            client.loop_start()
        except TimeoutError:
            logging.warning(f'sock.connect timeout on {current_thread().name}')
            return None
        except socket.gaierror:
            logging.warning(f'[Errno 1101] getaddr info failed on {current_thread().name}')
            return None
        return client

    def publish_any(self, dataset: csv.DictReader) -> None:
        client = self.connect_mqtt()
        for data_sample in dataset:
            if self.paused:
                time.sleep(self.interval)
                continue
            if self.stop:
                break
            json_data = json.dumps(data_sample, indent=4)
            time.sleep(self.interval)
            if self.protocol == 'mqtt':
                if client is None:
                    client = self.connect_mqtt()
                logging.warning(
                    f'mqtt: {self.app_name}: published topic {self.source_name} with inerval {self.interval}\n')
                # print(json_data)
                client.publish(self.source_name, json_data)
            if self.protocol == 'http':
                logging.warning(
                    f'http: {self.app_name}: published topic {self.source_name} with inerval {self.interval}\n')
                requests.post(f'{self.url}', json=json_data)
        return

    def callbacks(self):
        @self.sio.event
        def connect():
            logging.info(f'Connected {self.app_name}')
            self.sio.emit('register', {'name': self.app_name,
                                       'protocol': self.protocol,
                                       'interval': self.interval,
                                       'data_source': self.data_source,
                                       'url': self.url,
                                       'status': self.status,
                                       'uuid': self.uuid
                                       })

        @self.sio.on('update')
        def on_message(data):
            logging.info(f"New config: {data}")
            self.data_source = Path(data['data_source'])
            self.protocol = str(data['protocol'])
            self.url = str(data['url'])
            self.interval = float(data['interval'])

    def run_socketio(self):
        self.callbacks()
        self.sio.connect('http://localhost:5000', wait_timeout=10)

    def setup(self):
        self.register_app()
        thread = threading.Thread(target=self.run_socketio)
        thread.daemon = True
        thread.start()
        thread.join()

    def teardown(self):
        self.stop = True
        self.sio.disconnect()


def run_publishers(name, _uuid='2137', cfg='config_single.toml'):  # pragma: no cover
    config = load_config(cfg)
    threads = []
    publishers = []
    try:
        for app_config in config['app'].items():
            publisher_app = Publisher(app_name=app_config[0], **app_config[1])
            publishers.append(publisher_app)
            thread = Thread(target=publisher_app.start)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
    except TypeError:
        publisher_app = Publisher(app_name='Publisher', **config['app'])
        publisher_app.start()
        return publisher_app
    except KeyError:
        publisher_app = Publisher(app_name=name, uuid=str(_uuid), **config)
        thread = Thread(target=publisher_app.start)
        thread.daemon = True
        thread.start()
        # thread.join()
        return publisher_app

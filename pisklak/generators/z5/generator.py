import csv
import json
import logging
import socket
import threading
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse
import queue
import paho.mqtt.client as mqtt  # type: ignore
import requests
import toml


def load_config(conf_path: str | Path | dict = 'config.toml') -> dict:
    return conf_path if isinstance(conf_path, dict) else dict(toml.load(conf_path))


class Publisher:
    def __init__(self, data_source: str | Path = '', url: str = 'test.mosquitto.org', protocol: str = 'mqtt',
                 interval: float = 1, delim: str = ';', *, app_name: str = 'app', uuid: str = '2137',
                 manager: str = 'http://127.0.0.1:5000/register', address: str = None):
        self.paused = False
        self.stop = False
        self.data_source = data_source
        self.source_name: str = Path(data_source).stem
        self.url: str = url
        if not protocol.lower() in ('http', 'mqtt'):
            raise ValueError(f'Unsupported protocol: {url}')
        self.protocol: str = protocol.lower()
        self.interval: float = interval
        self.delim: str = delim
        self.app_name: str = app_name
        self.uuid = uuid
        self.address = address
        # SocketIO
        self.register_app(manager)
        # self.listener.join()

    @property
    def status(self) -> str:
        return 'paused' if self.paused else 'running'

    def register_app(self, manager: str):
        data = {
            'name': self.app_name,
            'protocol': self.protocol,
            'interval': self.interval,
            'data_source': self.data_source,
            'url': self.url,
            'uuid': self.uuid,
            'status': self.status,
            'address': self.address
        }
        requests.post(manager, data=data)
        # logging.warning(response.content)

    def __start(self, reader: csv.DictReader) -> None:
        self.publish_any(dataset=reader)

    def start(self) -> None:
        path = self.data_source
        if urlparse(str(path)).scheme in ('http', 'https'):
            dataset = urllib.request.urlopen(str(path)).read()
            reader = csv.DictReader(dataset, delimiter=self.delim)
            self.__start(reader)
            return
        try:
            with open(self.data_source, 'r', newline='') as dataset:
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
            logging.warning(f'sock.connect timeout on {threading.current_thread().name}')
            return None
        except socket.gaierror:
            logging.warning(f'[Errno 1101] getaddr info failed on {threading.current_thread().name}')
            return None
        return client

    def publish_any(self, dataset: csv.DictReader) -> None:
        client = None
        if self.protocol == 'mqtt':
            client = self.connect_mqtt()
        for data_sample in dataset:
            if self.paused:
                time.sleep(0.1)
                continue
            if self.stop:
                break
            json_data = json.dumps(data_sample, indent=4)
            time.sleep(self.interval)
            if self.protocol == 'mqtt':
                if client is None:
                    client = self.connect_mqtt()
                    if client is not None:
                        logging.warning(
                            f'mqtt: {self.app_name}: published topic {self.source_name} with inerval {self.interval}\n')
                        # print(json_data)
                        client.publish(self.source_name, json_data)
            if self.protocol == 'http':
                if client is not None:
                    client = None
                try:
                    logging.warning(
                        f'http: {self.app_name}: published topic {self.source_name} with inerval {self.interval}\n')
                    requests.post(f'{self.url}', json=json_data)
                except (requests.exceptions.InvalidURL, requests.exceptions.RequestException) as e:
                    logging.warning(f'http: {self.app_name}: {e}\n')
        return

    def teardown(self):
        self.stop = True

    def __str__(self):
        return str(self.app_name)

    def __repr__(self):
        return str(self.app_name)


def run_publishers(name: str = 'Generator', _uuid='2137', cfg='config_single.toml',
                   q: queue.Queue = None, *, address: str):  # pragma: no cover
    config = load_config(cfg)
    threads = []
    publishers = []
    try:
        for app_config in config['app'].items():
            publisher_app = Publisher(app_name=app_config[0], **app_config[1])
            publishers.append(publisher_app)
            thread = threading.Thread(target=publisher_app.start)
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
        publisher_app = Publisher(app_name=name, uuid=str(_uuid), **config, address=address)
        if q is not None:
            q.put(publisher_app)
        thread = threading.Thread(target=publisher_app.start)
        thread.daemon = True
        thread.start()
        # thread.join()
        return publisher_app

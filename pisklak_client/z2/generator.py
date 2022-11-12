import json

import paho.mqtt.client as mqtt
import time
import logging
import psutil
from datetime import datetime

import requests


def publish_single(broker: str = 'test.mosquitto.org') -> None:
    def on_connect(_client, _userdata, _flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt.Client('pisklak')
    client.username_pw_set('pisklak', 'aaa')
    client.on_connect = on_connect
    client.connect(broker, 443)


def publisher(broker: str = 'test.mosquitto.org') -> None:
    client = mqtt.Client('pisklak123')
    client.connect(broker, 1883)
    client.loop_start()

    class Usage:
        def __init__(self, usage: float) -> None:
            self._usage = usage
            self.timestamp = datetime.now().timestamp()

        @property
        def usage(self) -> float:
            return self._usage

        @usage.setter
        def usage(self, usage: float) -> None:
            self._usage = usage
            self.timestamp = datetime.now().timestamp()

        def changed(self, new: float) -> bool:
            if abs(new - self.usage) > 256:
                self.usage = new
                return True
            return False

    ram_data = Usage(psutil.virtual_memory()[3] / 1000000)
    while True:
        try:
            # send post data
            if ram_data.changed(psutil.virtual_memory()[3] / 1000000):
                ram_usage = f'{{"ram": "{ram_data.usage}","timestamp":"{ram_data.timestamp}"}}'
                client.publish('pisklak_ram', ram_usage)
                # publish.single('test', "payload", hostname=broker)
                print(f'Published: {ram_usage}')
            time.sleep(0.2)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.warning(e)
            break


def subscriber(broker: str = 'test.mosquitto.org') -> None:
    def on_connect(client, _userdata, _flags, rc):
        client.subscribe('pisklak_ram')
        print(f"Connection returned result: {mqtt.connack_string(rc)}")

    def on_message(_client, _userdata, msg):
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
    """
    from threading import Thread
    th2 = Thread(target=subscriber)
    th1 = Thread(target=publisher)
    th1.daemon = True
    th2.daemon = True
    th2.start()
    th1.start()
    th2.join()
    th1.join()
    """
    publish_single()

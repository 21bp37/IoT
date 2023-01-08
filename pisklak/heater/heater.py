import threading
import time

import requests
from flask import Blueprint, request, make_response


class ElectricHeater:
    mod: Blueprint = Blueprint('heater', __name__)
    interval: float = 4
    recorded_temps: list = []
    is_on: bool = False  # Aktuator DOMYŚLNIE OFF (False)
    room_temp: float = 0
    speed_up = 1
    temp: float = 0
    temperature: float = 0
    target: str = '127.0.0.1:5004'  # Adres sterownika

    @classmethod
    def send_current_temp(cls):
        requests.post(f'http://{cls.target}/send', data={'temperature': cls.temperature})

    @classmethod
    def status(cls):
        return cls.is_on

    @staticmethod
    @mod.route('/temps', methods=['GET', 'POST'])
    def temps_route():
        return str(ElectricHeater.recorded_temps)

    @staticmethod
    @mod.route('/temperature', methods=['GET', 'POST'])
    def current_temperature_route():
        return ElectricHeater.temperature

    @staticmethod
    @mod.route('/status', methods=['GET', 'POST'])
    def status_route():
        return make_response('Działa', 201) if ElectricHeater.status() else make_response('Nie działa', 200)

    @staticmethod
    @mod.route('/start', methods=['GET', 'POST'])
    def start_route():
        power = 1500  # domyslna
        if request.method == 'POST':
            power = float(request.form['power'])
        if not ElectricHeater.is_on:
            # ElectricHeater.is_on = True
            worker = threading.Thread(target=ElectricHeater.start, daemon=True, kwargs={'power': power})
            worker.start()
            return make_response('wystartowano', 200)
        return make_response('już był wystartowany', 200)

    @staticmethod
    @mod.route('/stop', methods=['GET', 'POST'])
    def stop_route():
        if ElectricHeater.is_on:
            # ElectricHeater.is_on = False
            worker = threading.Thread(target=ElectricHeater.stop, daemon=True)
            worker.start()
            return make_response('zatrzymano', 200)
        return make_response('już był zatrzymany', 200)

    @classmethod
    def start(cls, power: float):
        if cls.is_on:
            return
        cls.is_on = True
        print('włączono aktuator')
        while cls.temp < 0 and cls.is_on:
            cls.temperature += cls.speed_up * 3.33 * (10 ** -6) * power * cls.interval
            cls.recorded_temps.append(cls.temperature)
            cls.temp += cls.speed_up * 0.1 / cls.interval
            cls.send_current_temp()
            time.sleep(cls.interval)
        while cls.is_on:
            cls.temperature += cls.speed_up * 6.66 * (10 ** -6) * power * cls.interval
            cls.recorded_temps.append(cls.temperature)
            cls.send_current_temp()
            time.sleep(cls.interval)
        cls.temp = 4 if cls.temp >= 0 else cls.temp
        cls.stop()

    @classmethod
    def stop(cls):
        if not cls.is_on:
            return
        cls.is_on = False
        print('wyłączono aktuator')
        while cls.temp > 0 and not cls.is_on:
            # grzejnik nagrzewa sie przez pewien czas po wyłączeniu
            cls.temperature += cls.speed_up * 3.33 * (10 ** -6) * 750 * cls.interval
            cls.recorded_temps.append(cls.temperature)
            cls.temp -= cls.speed_up * 0.1 * cls.interval
            cls.send_current_temp()
            time.sleep(cls.interval)
        while cls.temperature > cls.room_temp and not cls.is_on:
            cls.temperature -= cls.speed_up * 3.33 * (10 ** -3) * cls.interval
            cls.recorded_temps.append(cls.temperature)
            cls.temperature = max(cls.temperature, cls.room_temp)
            cls.send_current_temp()
            time.sleep(cls.interval)
        cls.temp = -4 if cls.temp <= 0 else cls.temp

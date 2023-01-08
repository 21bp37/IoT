import threading
import requests
from flask import Blueprint, request, make_response


class Controller:
    def __init__(self, min_temp: float = 20, max_temp: float = 21, address: str = '127.0.0.1:5003') -> None:
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.target_address = address
        self.power = 1500
        worker = threading.Thread(target=self.run, daemon=True)
        worker.start()

    def update_config(self, min_temp: float = 20, max_temp: float = 21, address: str = '127.0.0.1:5003'):
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.target_address = address
        worker = threading.Thread(target=self.run, daemon=True)
        worker.start()

    def make_decision(self, temperature: float) -> bool:
        # False - wyłączenie
        # True - włączenie
        # status = request.get status grzejnika
        code = requests.get(f'http://{self.target_address}/status').status_code
        # print(temperature, code, self.max_temp, self.min_temp)
        # status = True if code == 201 else False
        """if temperature > self.max_temp:
                    return False
                if not status and temperature < self.min_temp:
                    return True
                return False"""
        if code == 201:
            if temperature > self.max_temp:
                requests.post(f'http://{self.target_address}/stop')
        elif code == 200:
            if temperature < self.min_temp:
                requests.post(f'http://{self.target_address}/start', data={'power': self.power})
        return False

    def run(self):
        requests.post(f'http://{self.target_address}/start', data={'power': self.power})


class ControllerRoutes:
    mod: Blueprint = Blueprint('controller', __name__)
    controller: Controller = None
    last_received = None

    @classmethod
    def start_controller(cls, config: dict):
        cls.controller = Controller(**config)

    @classmethod
    def update_config(cls, config: dict):
        try:
            cls.controller.update_config(**config)
        except (ValueError, KeyError):
            return

    @staticmethod
    @mod.route('/send', methods=['GET', 'POST'])
    def temps_route():
        if request.method == 'POST':
            if 'temperature' not in request.form:
                return 'Brak temperatury'
            temperature = float(request.form['temperature'])
            ControllerRoutes.last_received = temperature
            if ControllerRoutes.controller:
                ControllerRoutes.controller.make_decision(temperature)
                """
                controller = ControllerRoutes.controller
                code = requests.get(f'http://{controller.target_address}/status').status_code
                if decision and code == 200:
                    requests.post(f'http://{controller.target_address}/start', data={'power': controller.power})
                elif not decision and code == 201:
                    requests.post(f'http://{controller.target_address}/stop')
                return make_response('OK', 200)
                """
            return make_response('Nie zdefiniowano konfiguracji', 500)
        if ControllerRoutes.controller:
            if ControllerRoutes.last_received:
                return f'ostatnio otrzymana temperatura to {ControllerRoutes.last_received}'
            return 'nie otrzymano jeszcze zadnej tmeperatury'
        return 'brak konfiguracji'

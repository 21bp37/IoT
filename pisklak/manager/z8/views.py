import requests
from flask import Blueprint, request, make_response

mod = Blueprint('flask_z8', __name__)
# DEBUGOWANIE KODU - AUTOMATYCZNE WPISANIE GRZEJNIKA
heaters = ['127.0.0.1:5003']


# gen2 = []

@mod.route('/heater_register', methods=['GET', 'POST'])
def register_heater():
    if request.method == 'POST':
        try:
            address = request.form['address']
            heaters.append(address)
            # requests.post(f"http://{address}/")
        except KeyError:
            return 'missing config data'
    return str(heaters)


@mod.route('/on_heater', methods=['GET', 'POST'])
def on_heater():
    power = 1500
    address = '127.0.0.1:5003'  # domyslny adres na potrzebe debugowania kodu
    if request.method == 'POST':
        power = float(request.form['power'])
        address = request.form['address']
    requests.post(f'http://{address}/start', data={'power': power})
    return 'ok'


@mod.route('/heater_status', methods=['GET', 'POST'])
def heater_status():
    address = '127.0.0.1:5003'  # domyslny adres na potrzebe debugowania kodu
    if request.method == 'POST':
        address = request.form['address']
    code = requests.post(f'http://{address}/status').status_code
    return make_response('ok', code)
    # return make_response('w', 500)


@mod.route('/off_heater', methods=['GET', 'POST'])
def off_heater():
    # power = 1500
    address = '127.0.0.1:5003'  # domyslny adres na potrzebe debugowania kodu
    if request.method == 'POST':
        address = request.form['address']
    requests.post(f'http://{address}/stop')
    return 'ok'


@mod.route('/start_heater', methods=['GET', 'POST'])
def start_heater():
    if request.method == 'POST':
        try:
            address = request.form['address']
            heaters.append(address)
            requests.post(f"http://{address}/start_manager")
        except KeyError:
            return 'missing config data'
    else:
        """Debugowanie kodu - sprawdzenie działania przez get request:"""
        for heater in heaters:
            requests.post(f"http://{heater}/start_manager")
    return str(heaters)


@mod.route('/stop_heater', methods=['GET', 'POST'])
def stop_heater():
    if request.method == 'POST':
        try:
            address = request.form['address']
            heaters.append(address)
            requests.post(f"http://{address}/stop_manager")
            # requests.post(f"http://{address}/")
        except KeyError:
            return 'missing config data'
    else:
        """Debugowanie kodu - sprawdzenie działania przez get request:"""
        for heater in heaters:
            requests.post(f"http://{heater}/stop_manager")
    return str(heaters)

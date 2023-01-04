import math
import random
import datetime
import numpy
import csv


def generate_waves(n: int = 86400):
    data = []
    data_waves = {
        'time': [],
        'wave_height': [],  # 2.6m
        'average_period': [],  # 9s
    }
    data_wind = {
        'time': [],
        'wind_direction': [],
        'wind_speed': [],
        'wind_chill': []
    }
    data_visibility = {
        'time': [],
        'visibility': []
    }
    data_temperature = {
        'time': [],
        'temperature': []
    }
    data_atmospheric = {
        'time': [],
        'atmospheric_pressure': []
    }
    data_dict = {
        'time': [],
        'wind_direction': [],
        'wind_speed': [],
        'wind_chill': [],
        'wave_height': [],
        # 'average_period': [], # agregator
        'temperature': [],
        'visibility': [],
        'atmospheric_pressure': []
    }
    cdate = datetime.datetime(2022, 12, 12, 0, 0, 0, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
    hour = 0
    winds = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')
    winds_map = ((340, 380), (20, 70), (70, 110), (110, 160), (160, 200), (200, 250), (250, 290), (290, 340))
    deg = random.uniform(0, 360)
    wind_direction = None
    wind_chill = abs(numpy.random.normal(1, 0.2))
    curr_time = 0
    wind_speed = abs(numpy.random.normal(3.5, 1.5))
    data2 = []
    for wind in winds_map:
        if wind[0] <= deg <= wind[1]:
            wind_direction = winds[winds_map.index(wind)]
            break
    if not wind_direction:
        wind_direction = 'N'
    for i in range(n):  # range n
        # wind
        # interwał - losowy(?) (kiedy zaobserwowano falę)
        """if hour / 3600 >= 1:
            hour = 0
            wind_speed = abs(numpy.random.normal(3.5, 1.5))"""
        wind_speed = abs(numpy.random.normal(0, 0.007) + wind_speed)
        # direction
        deg += numpy.random.normal(0, 1.5)
        deg %= 380
        for wind in winds_map:
            if wind[0] <= deg <= wind[1]:
                wind_direction = winds[winds_map.index(wind)]
                break
        # chill:
        wind_chill += random.uniform(-0.005, 0.005)
        wind_chill = abs(wind_chill)

        # temperature
        noise = numpy.random.normal(0, 0.005)
        hrs = abs((cdate - cdate.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()) / 3600
        temperature = noise + 5.2 * abs(math.sin(hrs * math.pi / 24))
        # visibility
        noise = numpy.random.normal(0.01, 0.001)
        visibility = 58 + noise + 10 * math.sin((hrs - 2.3 + temperature * 0.25) * math.pi / 24)
        # pressure
        noise = numpy.random.normal(0.01, 0.005)
        pressure = 1024 + noise + 18 * math.sin((hrs - 1.8 + temperature * 0.25 + visibility / 68) * math.pi / 24)
        # increment

        # wave height
        if i % 24 == 0:
            pass
        h = 0.7*wind_speed
        t = numpy.random.rayleigh(scale=h)

        # date
        dt = abs(numpy.random.normal(8 + wind_speed * 0.15, wind_speed * 0.7))
        noise = abs(numpy.random.normal(0.02, 0.002))
        dt += min(noise, 0.4)
        cdate += datetime.timedelta(seconds=dt)
        hour += dt

        curr_time += dt / 3600  # godziny
        curr_time = curr_time % 24

        data_dict['time'].append(cdate)
        data_dict['wind_direction'].append(wind_direction)
        data_dict['wind_speed'].append(wind_speed)
        data_dict['wind_chill'].append(wind_chill)
        data_dict['wave_height'].append(t)
        data_dict['temperature'].append(temperature)
        data_dict['visibility'].append(visibility)
        data_dict['atmospheric_pressure'].append(pressure)
        new_data = {
            'time': cdate,
            'wind_direction': wind_direction,
            'wind_speed': wind_speed,
            'wind_chill': wind_chill,
            'wave_height': t,
            # 'average_period': [], # agregator
            'temperature': temperature,
            'visibility': visibility,
            'atmospheric_pressure': pressure
        }
        data2.append(new_data)
    return data2


if __name__ == '__main__':
    for i in range(5):
        new = generate_waves()
        columns = ['time',
                   'wind_direction',
                   'wind_speed',
                   'wind_chill',
                   'wave_height',
                   'temperature',
                   'visibility',
                   'atmospheric_pressure']
        try:
            with open(f'oil_rig{i}.csv', 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=columns)
                writer.writeheader()
                for info in new:
                    writer.writerow(info)
        except IOError:
            print("I/O error")

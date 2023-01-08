import time
import threading

from pisklak import run_manager, run_generator, run_aggregator, run_filter, run_heater, run_controller


def is_any_thread_alive(_threads: list[threading.Thread]) -> bool:
    return True in [t.is_alive() for t in _threads]


if __name__ == '__main__':
    # manager
    manager = run_manager()
    manager_thread = threading.Thread(target=manager.run, daemon=True, kwargs={'use_reloader': False, 'port': 5000})
    manager_thread.start()

    # threads
    threads = [manager_thread]
    """
    # generators
    for i in range(5):
        port = 5008 + i
        generator = run_generator(port=port, _id=i)
        generator_thread = threading.Thread(target=generator.run, daemon=True,
                                            kwargs={'use_reloader': False, 'port': port})
        threads.append(generator_thread)
        generator_thread.start()

    # uruchomienie usługi filtrującej:
    # adres filtru: locahlost:5002
    _filter = run_filter(port=5002)
    filter_thread = threading.Thread(target=_filter.run, daemon=True,
                                     kwargs={'use_reloader': False, 'port': 5002})
    filter_thread.start()
    threads.append(filter_thread)
    # generator_thread.join()
    # aggregator
    aggregator = run_aggregator(port=5001)
    aggregator_thread = threading.Thread(target=aggregator.run, daemon=True,
                                         kwargs={'use_reloader': False, 'port': 5001})
    aggregator_thread.start()
    threads.append(aggregator_thread)"""
    # kontroler
    controller = run_controller(port=5004)
    controller_thread = threading.Thread(target=controller.run, daemon=True,
                                         kwargs={'use_reloader': False, 'port': 5004})
    controller_thread.start()
    threads.append(controller_thread)

    # grzejnik
    heater = run_heater(port=5003)
    heater_thread = threading.Thread(target=heater.run, daemon=True,
                                     kwargs={'use_reloader': False, 'port': 5003})
    heater_thread.start()
    threads.append(heater_thread)

    while is_any_thread_alive(threads):
        time.sleep(0.1)

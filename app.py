import time
import threading

import requests

from pisklak import run_manager, run_generator, run_aggregator


def is_any_thread_alive(_threads: list[threading.Thread]) -> bool:
    return True in [t.is_alive() for t in _threads]


if __name__ == '__main__':
    # manager
    manager = run_manager()
    manager_thread = threading.Thread(target=manager.run, daemon=True, kwargs={'use_reloader': False, 'port': 5000})
    manager_thread.start()
    # aggregator
    aggregator = run_aggregator(port=5001)
    aggregator_thread = threading.Thread(target=aggregator.run, daemon=True,
                                         kwargs={'use_reloader': False, 'port': 5001})
    aggregator_thread.start()
    # threads
    threads = [manager_thread, aggregator_thread]
    # generators
    for i in range(5):
        port = 5002 + i
        generator = run_generator(port=port)
        generator_thread = threading.Thread(target=generator.run, daemon=True,
                                            kwargs={'use_reloader': False, 'port': port})
        threads.append(generator_thread)
        generator_thread.start()
    # generator_thread.join()
    while is_any_thread_alive(threads):
        time.sleep(0.1)

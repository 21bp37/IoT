import time
import threading
from pisklak import run_manager, run_generator


def is_any_thread_alive(_threads: list[threading.Thread]) -> bool:
    return True in [t.is_alive() for t in _threads]


if __name__ == '__main__':
    manager = run_manager()
    manager_thread = threading.Thread(target=manager.run, daemon=True, kwargs={'use_reloader': False, 'port': 5000})
    manager_thread.start()
    threads = [manager_thread]
    for i in range(5):
        port = 5001 + i
        generator = run_generator(port=port)
        generator_thread = threading.Thread(target=generator.run, daemon=True,
                                            kwargs={'use_reloader': False, 'port': port})
        threads.append(generator_thread)
        generator_thread.start()
    # generator_thread.join()
    while is_any_thread_alive(threads):
        time.sleep(0.1)

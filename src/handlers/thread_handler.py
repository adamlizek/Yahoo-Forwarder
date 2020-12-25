from threading import Thread
import config as CONFIG
import time


def spawn_threads(num_threads, action):
    print(num_threads)

    threads = []

    i = 1
    for _ in range(num_threads):
        threads.append(Thread(target=action, name=str(i)))
        i += 1

    for thread in threads:
        thread.start()
        time.sleep(CONFIG.DELAY_BETWEEN_THREAD_SPAWN)

    for thread in threads:
        thread.join()


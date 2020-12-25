import threading


class Thread(threading.Thread):
    def __init__(self, action, shared_memory):
        self.action = action
        self.shared_memory = shared_memory
        self.stop_flag = threading.Event()

    def start(self):
        self.pythread = threading.Thread(target=self.action, args=(self.stop_flag, self.shared_memory), daemon = True)
        self.pythread.start()

    def stop(self):
        self.stop_flag.set()

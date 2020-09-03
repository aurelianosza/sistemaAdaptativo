import multiprocessing
import socket
import json


class reconfiguration_sm:
    def __init__(self, sender_queue_above, receiver_queue_above, sender_queue_below, receiver_queue_below):
        self.strategies = {}
        self.sender_above = sender_queue_above
        self.receiver_above = receiver_queue_above

        self.sender_below = sender_queue_below
        self.receiver_below = receiver_queue_below

    def add_strategy(self, name, strategy):
        self.strategies[name] = strategy

    def read_strategy(self, name):
        return self.strategies[name]

    def run_strategy(self, name):
        self.sender_below.put(self.strategies[name])

    def recv_commands(self):
        while True:
            command = self.receiver_above.get()
            if command["type"] == "add":
                self.add_strategy(command["name"], command)
            elif command["type"] == "run":
                self.run_strategy(command["name"])

    def recv_response(self):
        while True:
            aux = self.receiver_below.get()
            self.sender_above.put(aux)

    def run(self):
        multiprocessing.Process(target=self.recv_commands).start()
        multiprocessing.Process(target=self.recv_response).start()


if __name__ == "__main__":
    sender = multiprocessing.Queue()
    recv = multiprocessing.Queue()

    reconfiguration_sm(sender, recv).run()

    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sc.bind(("0.0.0.0", 10223))

    sc.listen(1)

    def receptor(queue):
        while True:
            print("output {}\n".format(queue.get()))

    multiprocessing.Process(target=receptor, args=(sender,)).start()

    aux, addr = sc.accept()

    while True:
        command = aux.recv(1024).decode()
        recv.put(json.loads(command))

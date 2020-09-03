import multiprocessing
import json
import socket


class behaviour_sm:
    def __init__(self, sender_queue_above, receiver_queue_above, sender_queue_below, receiver_queue_below):
        self.events = {}

        self.sender_above = sender_queue_above
        self.receiver_above = receiver_queue_above

        self.sender_below = sender_queue_below
        self.receiver_below = receiver_queue_below

    def create_event(self, name, event):
        self.events[name] = event

    def active_event(self, name):
        aux = self.events[name]
        aux["type"] = "create"
        self.sender_below.put(aux)

    def disable_events(self, name):
        self.sender_below.put({"type": "delete", "name": name})

    def recv_comands(self):
        while True:
            command = self.receiver_above.get()

            if command["type"] == "create":
                self.create_event(command["name"], command)
            elif command["type"] == "active":
                self.active_event(command["name"])
            elif command["type"] == "disable":
                self.disable_events(command["name"])

    def recv_events(self):
        while True:
            aux = self.receiver_below.get()
            self.sender_above.put(aux)

    def run(self):
        multiprocessing.Process(target=self.recv_comands).start()
        multiprocessing.Process(target=self.recv_events).start()


if __name__ == "__main__":
    sender = multiprocessing.Queue()
    receiver = multiprocessing.Queue()

    def verify_sender(queue):
        while True:
            print("output \n {}".format(queue.get()))

    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sc.bind(("0.0.0.0", 12312))

    multiprocessing.Process(target=verify_sender, args=(sender,)).start()

    sc.listen(1)

    aux, addr = sc.accept()

    bsm = behaviour_sm(sender, receiver)
    bsm.run()

    while True:
        command = aux.recv(1024).decode()
        command = json.loads(command)
        receiver.put(command)

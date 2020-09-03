import multiprocessing
import command.command


class reconfiguration_se(object):
    def __init__(self, sender_queue_above, receiver_queue_above, sender_queue_below, receiver_queue_below, mutex):
        self.sender_above = sender_queue_above
        self.receiver_above = receiver_queue_above
        self.sender_below = sender_queue_below
        self.receiver_below = receiver_queue_below
        self.command_facade = command.command.command_facade()
        self.mutex = mutex

    def run(self):
        t1 = multiprocessing.Process(target=self.recv_commands)
        t1.start()

    def recv_commands(self):
        while True:
            data = self.receiver_above.get()
            self._execute_strategy(data)

    def _execute_strategy(self, data):
        try:
            command = self.command_facade.get_command(data)
            aux = command.command_txt()
            self.mutex.acquire()
            self.sender_below.put(aux)
            aux = self.receiver_below.get()
            self.mutex.release()

            if command.type_response() == 'string':
                aux = aux.replace("\n", '')
            elif command.type_response() == 'int':
                aux = int(aux)
            elif command.type_response() == 'float':
                aux = float(aux)

            if 'expected' in data:
                if data['expected'] == aux:
                    self.sender_above.put({'type': 'success'})
                else:
                    self.sender_above.put(
                        {'type': 'exception', 'command': data['name']})
            else:
                self.sender_above.put({'type': 'response', 'value': aux})

        except Exception as e:
            self.sender_above.put(str(e))

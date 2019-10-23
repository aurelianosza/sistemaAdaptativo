import multiprocessing
import command.command 

class reconfiguration_se(object):
    def __init__(self, socket, sender_queue, receiver_queue):
        self._sock = socket
        self.sender = sender_queue
        self.receiver = receiver_queue
        self.command_facade = command.command.command_facade()

    # """
    #     _run
    #     - Executa o loop responsavel pela execução do componente
    #     - @return none
    # """
    def run(self):
        t1 = multiprocessing.Process(target=self.recv_commands)
        t1.start()

    def recv_commands(self):
        while True:
            data = self.receiver.get()
            self._execute_strategy(data)

    # """
    #     execute_etrategy
    #     - Executa uma stratégia a partir do 
    #     - @param    string  name    - nome da estrategia
    #     - @return   none
    # """
    def _execute_strategy(self, data):
        try:
            for i in data:
                aux = self.command_facade.get_command(i)
                response = self._send_command(aux)
                print(response)
        except Exception as e:
            print(e)
            self.sender.put(str(e))

    
    def _send_command(self, command):
        self._sock.send(command.command_txt().encode())
        data = self._sock.recv(1024)
        return data.decode()

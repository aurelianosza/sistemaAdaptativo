import json
import socket

class interface(object):

    def __init__(self):
        self._modules = {}
        
    def send_command(self, command, args):
        pass

    def add_module(self, name, module):
        self._modules['name'] = module

    def get_instance(type):
        if type == "http":
            return http_interface()
        elif type == "socket":
            return socket_interface()

    get_instance = staticmethod(get_instance)

class socket_interface(interface):
    def __init__(self):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def send_command(self, command, args):
        part = command
        for i in args:
            part = part + " {}".format(i)
        print(part)

class http_interface(interface):
    def send_command(self, command, args):
        array = {}
        array['command'] = command
        array['args'] = args
        print(json.dumps(array))
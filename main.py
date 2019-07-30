from interface_factory.interface import interface
import command.command
import json
import socket
import _thread

class main(object):
    def __init__(self):
        self.modules = {}
        self.server = {}
        self.commands = {}
        self.file_config = ''
        self.target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        with open('ini.json') as config:
            cfg = json.loads(config.read())
            self.target.connect((cfg["target"]["host"], cfg["target"]["port"]))

            for i in cfg['server']:
                self.server['principal'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server['principal'].bind((i['host'], int(i['port'])))
                self.server['principal'].listen(5)


            with open(cfg['config']) as modules_json:
                modules = json.loads(modules_json.read())
                for i in modules['modules']:
                    self.modules[i['name']] = []
                    for j in i['commands']:
                        self.modules[i['name']].append(command.command.comand(j))
                        self.commands[j['command']] = self.modules[i['name']][-1]

        
        print("System listen in {}".format(self.server['principal'].getsockname()))

        while True:
            try:
                sock, addr = self.server['principal'].accept()
                _thread.start_new_thread(self.recv_commands, (sock,))
            except KeyboardInterrupt:
                self.target.close()
                break

            

    def recv_commands(self,sock):
        while True:
            data = sock.recv(1024)
            try:
                data = json.loads(data.decode())
                if not "command" in data or not"params" in data:
                    raise ValueError('Syntax err !!\n')

                if data["command"] in self.commands:
                    aux = self.commands[data["command"]].copy()
                    aux.load_paramets(data["params"])

                    if aux.validate():
                        sock.send(self.send_command(aux).encode())
                    else:
                        raise ValueError('Params does not match !\n')

                else:
                    raise ValueError('Command not found\n')

            except ValueError as err:
                sock.send(str(err).encode())
            except Exception:
                sock.send("Err do not knowedge !!\n".encode())
            except KeyboardInterrupt:
                sock.close()
                break
            finally:
                pass
            
    def send_command(self, command):
        self.target.send(command.command_txt().encode())
        data = self.target.recv(1024)
        return data.decode()


    def load_modules(self, file):
        pass


if __name__ == '__main__':
    main()
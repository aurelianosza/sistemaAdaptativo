from interface_factory.interface import interface
from apscheduler.schedulers.background import BackgroundScheduler
import command.command
import json
import socket
from threading import Thread
import _thread


class main(object):
    def __init__(self):
        self.modules = {}
        self.server_comandos = {}
        self.server_eventos = {}
        self.events = {}
        self.commands = {}
        self.file_config = ''
        self.server_threads = []

        self.target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.event_scheduler = BackgroundScheduler()
        self.event_scheduler.start()

        with open('ini.json') as config:
            cfg = json.loads(config.read())
            self.target.connect((cfg["target"]["host"], cfg["target"]["port"]))

            for i in cfg['server']:
                if i['function'] == 'comandos':
                    self.server_comandos[i['name']] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.server_comandos[i['name']].bind((i['host'], int(i['port'])))
                elif i['function'] == 'eventos':
                    self.server_eventos[i['name']] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.server_eventos[i['name']].bind((i['host'], int(i['port'])))


            with open(cfg['config']) as modules_json:
                modules = json.loads(modules_json.read())
                for i in modules['modules']:
                    self.modules[i['name']] = []
                    for j in i['commands']:
                        self.modules[i['name']].append(command.command.comand(j))
                        self.commands[j['command']] = self.modules[i['name']][-1]


    def add_event(self, event, sock):
        try:
            aux = None
            if event["command"] in self.commands:
                aux = self.commands[event["command"]].copy()
                aux.load_paramets(event['params'])
            else:
                sock.send("Erro Evento não existe".encode())
                return
            self.events[event['name']] = (self.event_scheduler.add_job(lambda:self.run_event(event['name'], event['operator'], int(event['base_value']), aux, sock), 'interval', seconds=int(event['interval'])), event)
        except Exception:
            sock.send("Error ao adicionar evento {}.".format(event['name']).encode())
        finally:
            pass

    def read_event(self, event, sock):
        try:
            if event['name'] in self.events:
                sock.send(json.dumps(self.events[event['name']][1]).encode())
            else:
                sock.send("Event not found".encode())
        except Exception:
            sock.send("Erro ao buscar evento".encode())

    def delete_event(self, event, sock):
        try:
            if event['name'] in self.events:
                self.events[event['name']][0].remove()
                del self.events[event['name']]
            else:
                sock.send("Event not Found".encode())
        except Exception:
            sock.send("Erro ao deletar evento".encode())

    def update_event(self, event, sock):
        try:
            if event['name'] in self.events:
                self.delete_event(event, sock)
                self.add_event(event, sock)
            else:
                sock.send("Event not found".encode())
        except Exception:
            sock.send("Erro ao atualizar evento")

    def run_event(self, name, operator, base_value, command, sock):
        aux = int(self.send_command(command))
        try:
            if operator == '==':
                if aux == base_value:
                    sock.send(name.encode())
            elif operator == '!=':
                if aux != base_value:
                    sock.send(name.encode())      
            elif operator == '>':
                if aux > base_value:
                    sock.send(name.encode())
            elif operator == '>=':
                if aux >= base_value:
                    sock.send(name.encode())
            elif operator == '<':
                if aux < base_value:
                    sock.send(name.encode())
            elif operator == '<=':
                if aux <= base_value:
                    sock.send(name.encode())
        except Exception:
            pass
        finally:
            pass



    def start_server_command(self, name):
        self.server_comandos[name].listen(5)
        print("Commands server {} listen in {}".format(name, self.server_comandos[name].getsockname()))
        while True:
            try:
                sock, addr = self.server_comandos[name].accept()
                _thread.start_new_thread(self.recv_commands, (sock,))
            except KeyboardInterrupt:
                self.target.close()
                break

    def start_server_evento(self, name):
        self.server_eventos[name].listen(5)
        print("Events server {} listen in {}".format(name, self.server_eventos[name].getsockname()))
        while True:
            try:
                sock, addr = self.server_eventos[name].accept()
                _thread.start_new_thread(self.recv_eventos, (sock,))
            except KeyboardInterrupt:
                pass


    def start(self):
        for key, values in self.server_comandos.items():
            i = Thread(target=self.start_server_command, args=(key,))
            i.start()
            self.server_threads.append(i)
        for key, values in self.server_eventos.items():
            j = Thread(target=self.start_server_evento, args=(key,))
            j.start()
            self.server_threads.append(j)
        for k in self.server_threads:
            k.join()

    def recv_eventos(self, sock):
        while True:
            data = sock.recv(1024)
            try:
                data = json.loads(data.decode())
                if data['type'] == 'create':
                    self.add_event(data,sock)
                elif data['type'] == 'read':
                    self.read_event(data,sock)
                elif data['type'] == 'delete':
                    self.delete_event(data, sock)
                elif data['type'] == 'update':
                    self.update_event(data, sock)
            except Exception:
                sock.send('Erro no evento'.encode())
            

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


if __name__ == '__main__':
    servidor = main()
    servidor.start()
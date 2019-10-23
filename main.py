from interface_factory.interface import interface
from apscheduler.schedulers.background import BackgroundScheduler
from reconfiguration_se import reconfiguration_se
from behaviour_se import behaviour_se
import command.command
import json
import socket
from threading import Thread
import _thread
import multiprocessing


class main(object):
    def __init__(self):
        self.modules = {}
        self.server_comandos = {}
        self.server_eventos = {}
        self.events = {}
        self.commands = {}
        self.file_config = ''
        self.server_threads = []


        self.queue = multiprocessing.Queue()

        self.queue_events_send = multiprocessing.Queue()
        self.queue_events_recv = multiprocessing.Queue()

        self.queue_commands_send = multiprocessing.Queue()
        self.queue_commands_recv = multiprocessing.Queue()

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
                facade = command.command.command_facade()
                facade.load_commands(modules)

    def close(self):
        self.target.close()
        for key, val in self.server_comandos:
            val.close()

        for key, val in self.server_eventos:
            val.close()

    def start(self):
        try:
            facade_eventos = multiprocessing.Process(target=self.start_server_event)
            facade_comandos = multiprocessing.Process(target=self.start_server_command)

            behaviour_se.behaviour_se(self.target, self.queue_events_send, self.queue_events_recv).run()
            reconfiguration_se.reconfiguration_se(self.target, self.queue_commands_send, self.queue_commands_recv).run()

            thread_exceptions = multiprocessing.Process(target=self.exceptions)

            facade_eventos.start()
            facade_comandos.start()
            thread_exceptions.start()

            facade_eventos.join()
            facade_comandos.join()
            thread_exceptions.join()


        except Exception as e:
            print(e)
            self.close()
        finally:
            pass

    def start_server_command(self):
            self.server_comandos['principal'].listen(1)
            print("Commands server principal listen in {}".format(self.server_comandos['principal'].getsockname()))

            while True:
                try:
                    sock, addr = self.server_comandos['principal'].accept()
                    self.command_facade(sock, self.queue_commands_recv)
                except KeyboardInterrupt:
                    self.target.close()
                    break

    def command_facade(self, client, queue):
        while True:
            data = client.recv(1024).decode()
            try:
                data = json.loads(data)
                queue.put(data)
            except Exception as err:
                print('erro {}'.format(err))
                client.send("Algum erro aconteceu, verifique a estrategia enviado erro {}".format(err).encode())
            finally:
                pass



    def start_server_event(self):
        self.server_eventos['secundario'].listen(1)
        print("Commands server secundario listen in {}".format( self.server_eventos['secundario'].getsockname()))

        client, addr = self.server_eventos['secundario'].accept()

        self.event_facade(client, self.queue_events_send)


    def event_facade(self, client, queue):
        while True:
            data = client.recv(1024).decode()
            try:
                
                data = json.loads(data)
                queue.put(data)

            except Exception as err:
                print('erro {}'.format(err))
                client.send("Algum erro aconteceu, verifique o comando enviado erro {}".format(err).encode())

            finally:
                pass
    
    def exceptions(self):
        while True:
            data = self.queue_events_recv.get()
            print(data)

        

    # def recv_commands(self,sock):


    #     while True:
    #         data = sock.recv(1024)
    #         try:
    #             data = json.loads(data.decode())
    #             if not "command" in data or not"params" in data:
    #                 raise ValueError('Syntax err !!\n')

    #             if data["command"] in self.commands:
    #                 aux = self.commands[data["command"]].copy()
    #                 aux.load_paramets(data["params"])

    #                 if aux.validate():
    #                     sock.send(self.send_command(aux).encode())
    #                 else:
    #                     raise ValueError('Params does not match !\n')

    #             else:
    #                 raise ValueError('Command not found\n')

    #         except ValueError as err:
    #             sock.send(str(err).encode())
    #         except Exception:
    #             sock.send("Err do not knowedge !!\n".encode())
    #         except KeyboardInterrupt:
    #             sock.close()
    #             break
    #         finally:
    #             pass
            
    def send_command(self, command):
        self.queue.put(command)
        self.target.send(command.command_txt().encode())
        data = self.target.recv(1024)
        return data.decode()

    # def reconfiguration_system_enactor(self, queue_receiver, queue_sender):
    #     while True:
    #         cmd = queue_receiver.get()
    #         self.target.send(cmd.command_txt().encode())
    #         data = self.target.recv(1024)
    #         queue_sender.put(data)


if __name__ == '__main__':
    servidor = main()
    servidor.start()

from interface_factory.interface import interface
from apscheduler.schedulers.background import BackgroundScheduler
from reconfiguration_se import reconfiguration_se
from behaviour_se import behaviour_se
from reconfiguration_sm import behaviour_sm
from goal import goal
import command.command
from reconfiguration_sm import reconfiguration_sm
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
        self.file_config = ""
        self.server_threads = []

        self.queue_target_up = multiprocessing.Queue()
        self.queue_target_down = multiprocessing.Queue()

        self.queue_rs_up = multiprocessing.Queue()
        self.queue_rs_down = multiprocessing.Queue()

        self.queue_bs_up = multiprocessing.Queue()
        self.queue_bs_down = multiprocessing.Queue()

        self.queue_bsm_rsm = multiprocessing.Queue()

        self.queue_goal_rsm_up = multiprocessing.Queue()
        self.queue_goal_rsm_down = multiprocessing.Queue()

        self.queue_goal_bsm_up = multiprocessing.Queue()
        self.queue_goal_bsm_down = multiprocessing.Queue()

        self.target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.event_scheduler = BackgroundScheduler()
        self.event_scheduler.start()

        self.mutex_target = multiprocessing.Lock()
        self.mutex_gm = multiprocessing.Lock()

        with open("ini.json") as config:
            cfg = json.loads(config.read())
            self.target.connect((cfg["target"]["host"], cfg["target"]["port"]))

            for i in cfg["server"]:
                if i["function"] == "comandos":
                    self.server_comandos[i["name"]] = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM
                    )
                    self.server_comandos[i["name"]].setsockopt(
                        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
                    )
                    self.server_comandos[i["name"]].bind(
                        (i["host"], int(i["port"])))
                elif i["function"] == "eventos":
                    self.server_eventos[i["name"]] = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM
                    )
                    self.server_eventos[i["name"]].setsockopt(
                        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
                    )
                    self.server_eventos[i["name"]].bind(
                        (i["host"], int(i["port"])))

            with open(cfg["config"]) as modules_json:
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
            facade_eventos = multiprocessing.Process(
                target=self.start_server_event)
            facade_comandos = multiprocessing.Process(
                target=self.start_server_command)

            self.start_behaviour_strategy_enactor()
            self.start_behaviour_strategy_manager()
            self.start_reconfiguration_strategy_enactor()
            self.start_reconfiguration_strategy_manager()
            self.start_send_target()

            #thread_exceptions = multiprocessing.Process(target=self.exceptions)

            facade_eventos.start()
            facade_comandos.start()
            # thread_exceptions.start()

            self.start_goal()

            facade_eventos.join()
            facade_comandos.join()
            thread_exceptions.join()

        except Exception as e:
            print(e)
            self.close()
        finally:
            pass

    def start_server_command(self):
        self.server_comandos["principal"].listen(1)
        print(
            "Commands server principal listen in {}".format(
                self.server_comandos["principal"].getsockname()
            )
        )

        while True:
            try:
                sock, addr = self.server_comandos["principal"].accept()
                self.command_facade(sock, self.queue_goal_rsm_down)
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
                print("erro {}".format(err))
                client.sendall(
                    "Algum erro aconteceu, verifique a estrategia enviado erro {}".format(
                        err
                    ).encode()
                )
            finally:
                pass

    def command_facade_return(self, client, queue):
        while True:
            data = queue.get()
            client.sendall(data.encode())

    def start_send_target(self):
        multiprocessing.Process(target=self.send_target, args=(
            self.queue_target_up, self.queue_target_down)).start()

    def start_behaviour_strategy_enactor(self):
        behaviour_se.behaviour_se(
            self.queue_bs_up, self.queue_bs_down, self.queue_target_down, self.queue_target_up, self.mutex_target
        ).run()

    def start_behaviour_strategy_manager(self):
        behaviour_sm.behaviour_sm(
            self.queue_goal_bsm_up, self.queue_goal_bsm_down, self.queue_bs_down, self.queue_bs_up).run()

    def start_reconfiguration_strategy_enactor(self):
        reconfiguration_se.reconfiguration_se(
            self.queue_rs_up, self.queue_rs_down, self.queue_target_down, self.queue_target_up, self.mutex_target
        ).run()

    def start_reconfiguration_strategy_manager(self):
        reconfiguration_sm.reconfiguration_sm(
            self.queue_goal_rsm_up, self.queue_goal_rsm_down, self.queue_rs_down, self.queue_rs_up
        ).run()

    def start_goal(self):
        goal.goal(self.queue_goal_rsm_up, self.queue_goal_rsm_down,
                  self.queue_goal_bsm_up, self.queue_goal_bsm_down).run()

    def start_server_event(self):
        self.server_eventos["secundario"].listen(1)
        print(
            "Commands server secundario listen in {}".format(
                self.server_eventos["secundario"].getsockname()
            )
        )

        client, addr = self.server_eventos["secundario"].accept()

        self.event_facade(client, self.queue_goal_bsm_down)

    def event_facade(self, client, queue):
        while True:
            data = client.recv(1024).decode()
            try:
                data = json.loads(data)

                queue.put(data)

            except Exception as err:
                print("erro {}".format(err))
                client.send(
                    "Algum erro aconteceu, verifique o comando enviado erro {}".format(
                        err
                    ).encode()
                )

            finally:
                pass

    def exceptions(self):
        while True:
            data = self.queue_bs_up.get()

    def send_target(self, sender, receiver):
        while True:
            aux = receiver.get()

            self.target.sendall(aux.encode())
            aux = self.target.recv(1024).decode()

            sender.put(aux)


if __name__ == "__main__":
    servidor = main()
    servidor.start()

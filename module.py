import json
import sys
from command.command import comand

class module(object):
    def __init__(self, name):
        self.commands = {}
        self.name = name

    def add_command(self, data):
        self.commands[aux['command']] = comand(data)

    def info(self):
        aux = {}
        for key, element in self.commands.items():
            aux[key] = element.description

        return json.dumps(aux)


if __name__ == '__main__':
    m = module("operacoes")
    m.add_command({command: "get_utilization",description	: "Retorna a utilizacao do servidor a partir do Id passado",params: [{name: "serverId",type: "int",description:"Id do servidor pesquisado"}],response:"float"})

    print(m.info())

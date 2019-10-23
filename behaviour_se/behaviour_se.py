import multiprocessing

from apscheduler.schedulers.background import BackgroundScheduler

import command.command 


class behaviour_se(object):
    def __init__(self,sock, queue_receiver, queue_sender):
        self._sock = sock
        self._revceiver = queue_receiver
        self._sender = queue_sender
        self._events = {}

        self.event_scheduler = BackgroundScheduler()
        self.command_facade = command.command.command_facade()


    def run(self):
        t1 = multiprocessing.Process(target=self.recv_eventos)
        t1.start()
    

    #"""
    #   recv_eventos - le os eventos da fila e faz o crud no sistema
    #"""
    def recv_eventos(self):
        self.event_scheduler.start()

        while True:
            data = self._revceiver.get()

            try:
                if data['type'] == 'create':
                    aux = self.command_facade.get_command(data)
                    if aux != False:
                        self.add_event(data['name'], data['operator'], data['base_value'], data['interval'], aux)

                if data['type'] == 'delete':
                    self.delete_event(data['name'])

                if data['type'] == 'update':
                    aux = self.command_facade.get_command(data)
                    if aux != False:
                        self.update_event(data['name'], data['operator'], data['base_value'], data['interval'], aux)

                
            except Exception:
                self._sender('Erro no evento')

    # """
    #     add_event - adiciona um evento para que o componente monitore o sistema alvo
    #     @param    string      name : nome do evento,
    #     @param    string      operator: operador para comparar com o resultado do evento ( > | < | <= | >= | == | !=),
    #     @param    number      base_value: Valor base de comparação com o evento,
    #     @param    int         interval: tempo de intervalo das requisiçõs para evento
    #     @param    command     command command - commando a ser executado
    # """
    def add_event(self, name, operator, base_value, interval, command):
        try:
            self._events[name] = self.event_scheduler.add_job(lambda:self._run_event(name, operator, base_value, command), 'interval', seconds=int(interval))
        except Exception as err:
            print("Erro ao adicionar evento {}".format(err))
        finally:
            pass

    #"""
    #   delete event - exclui um evento
    #   @param  string  name : nome do eventno para ser excluido
    #"""
    def delete_event(self, name):
        try:
            if name in self._events:
                self._events[name].remove()
                del self._events[name]
            else:
                self._sender.put("Evento não encontrado")
        except Exception:
            self._sender("Erro ao deletar evento")
        
    # """
    #     update_event - atualiza um evento para que o componente monitore o sistema alvo
    #     @param    string      name : nome do evento,
    #     @param    string      operator: operador para comparar com o resultado do evento ( > | < | <= | >= | == | !=),
    #     @param    number      base_value: Valor base de comparação com o evento,
    #     @param    int         interval: tempo de intervalo das requisiçõs para evento
    #     @param    command     command command - commando a ser executado
    # """
    def update_event(self, name, operator, base_value, interval, command):
        try:
            if name in self._events:
                self.delete_event(name)
                self.add_event(name, operator, base_value, interval, command)
            else:
                self._sender.put("Event not found")
        except Exception:
                self._sender.put("Erro ao atualizar evento")
            
    

    # """
    #     send_command - Envia um  comando ao sistema alvo
    #     @param command command - comando para ser enviado para o sistema alvo
    #     @return resposta do sistema ao receber o dado
    # """           
    def _send_command(self, command):
        self._sock.send(command.command_txt().encode())
        data = self._sock.recv(1024)
        return data.decode()

    # """
    #     run_event - Compara o resultado de um evento com um valor pre-definido
    #     @param name string - nome ao ser enviado para avisar a ocorrencia de um commando
    #     @param operator string(==, !=, >, <, >=, <=) - compara o do comando
    #     @param base_value numeric, valor para fazer a comparação
    #     @param commando command commando a ser enviado
    # """
    def _run_event(self, name, operator, base_value, command):
       
        aux = self._send_command(command)
        if command.type_response() == 'int':
            aux = int(aux)
        elif command.type_response() == 'float':
            aux = float(aux)
        try:
            if operator == '==':
                if aux == base_value:
                    self._sender.put(name)
            elif operator == '!=':
                if aux != base_value:
                    self._sender.put(name)   
            elif operator == '>':
                if aux > base_value:
                   self._sender.put(name)
            elif operator == '>=':
                if aux >= base_value:
                    self._sender.put(name)
            elif operator == '<':
                if aux < base_value:
                    self._sender.put(name)
            elif operator == '<=':
                if aux <= base_value:
                    self._sender.put(name)
        except Exception:
            pass
        finally:
            pass

#parametros
class parameter(object):
    def __init__(self):
       pass

    def validate(self):
        pass

    def set_value(self, value):
        pass

    def val(self):
        pass


class int_parameter(parameter):
    def __init__(self, name, description):
        super().__init__()
        self.value = 0
        self.name = name
        self.description = description

    def validate(self):
        return isinstance(self.value, int)

    def set_value(self, value):
        self.value = value

    def val(self):
        return self.value

class float_parameter(parameter):
    def __init__(self, name, description):
        super().__init__()
        self.value = 0.0
        self.name = name
        self.description = description

    def validate(self):
        return isinstance(self.value, float)

    def set_value(self, value):
        self.value = value

    def val(self):
        return self.value

class parameter_factory(object): 
    def __init__(self):
        pass

    def get_instance(type, name, description):
        if type == 'int':
            return int_parameter(name, description)
        elif type == 'float':
            return float_parameter(name, description)
        else:
            return None

    get_instance = staticmethod(get_instance)

#comandos
class comand(object):
    def __init__(self, data):
        self.instance = data
        self.paramets = {}
        self.name = data['command']
        self.description = data['description']
        self.response = data['response']
        for i in data['params']:
            self.paramets[i['name']] = parameter_factory.get_instance(i['type'], i['name'], i['description'])

    def load_paramets(self, data):
        for key, value in data.items():
            self.paramets[key].set_value(value)

    def validate(self):
        for key, val in self.paramets.items():
            if not self.paramets[key].validate():
                return False
        return True

    def copy(self):
        return comand(self.instance)

    def type_response(self):
        return self.response

    #send Command
    def command_txt(self):
        aux = self.name
        for key, value in self.paramets.items():
            aux = "{} {}".format(aux, value.val())
        
        return aux


if __name__ == '__main__':
    x = {"command":"get_utilization","description"	: "Retorna a utilização do servidor a partir do Id passado","params": [{"name"	: "serverId","type"	: "int","description": "Id do servidor pesquisado"}],"response"	: "float" }
    c = comand(x)
    c = c.copy()
    c.load_paramets({"serverId":10})
    print(c.command_txt())

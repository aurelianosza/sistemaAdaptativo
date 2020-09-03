import multiprocessing
import json


class goal(object):

    def __init__(self, queue_rsm_up, queue_rsm_down, queue_bsm_up, queue_bsm_down):
        self.rsm_up = queue_rsm_up
        self.rsm_down = queue_rsm_down
        self.bsm_up = queue_bsm_up
        self.bsm_down = queue_bsm_down

        self.mutex = multiprocessing.Lock()

        self.resolvers_reconfiguration = []
        self.resolvers_behaviour = []

        self.events = {}

        self.loads_resolvers()

    def loads_resolvers(self):
        with open("goal.json") as config:
            cfg = json.loads(config.read())
            for i in cfg['onInit']['behaviour']:
                self.bsm_down.put(i)

            for i in cfg['onInit']['reconfiguration']:
                self.rsm_down.put(i)

            self.events = cfg['resolversReconfiguration']

    def resolve_events(self, event_name):
        if event_name in self.events:
            for i in self.events[event_name]['behaviour']:
                self.bsm_down.put(i)
            for i in self.events[event_name]['reconfiguration']:
                self.rsm_down.put(i)

    def recv_rsm(self):
        while True:
            aux = self.rsm_up.get()

    def recv_bsm(self):
        while True:
            aux = self.bsm_up.get()
            self.resolve_events(aux['name'])

    def run(self):
        self.t_rsm = multiprocessing.Process(target=self.recv_rsm)
        self.t_bsm = multiprocessing.Process(target=self.recv_bsm)

        self.t_rsm.start()
        self.t_bsm.start()

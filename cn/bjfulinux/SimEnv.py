import random
import time
from cn.bjfulinux.Node import Node
import simpy
from cn.bjfulinux.Neigbhor_discover_finished import Neighbor_discover_finished
from cn.bjfulinux.commontools.primes import Primes



class SimEnv(simpy.Environment):
    def __init__(self, noise_thre):
        simpy.Environment.__init__(self)
        self.nodes = []
        self.NOISE_THRE = noise_thre

    def env_init(self, conf, protocol, classifier=None):
        self.TRANS_POWER = conf.get('topo', 'trans_power')
        self.MIN_RCV_RSSI = conf.get('topo', 'min_rcv_rssi')  # http://www.docin.com/p-266689616.html
        self.DUTYCYCLE_UPPER = conf.get('simulation', 'dutycycle_upper')
        self.DUTYCYCLE_LOWER = conf.get('simulation', 'dutycycle_lower')
        self.TIME_SLOT = round(float(conf.get('simulation', 'time_slot_milli')) / 1000, 3)

        self.wireless_channel = simpy.Resource(self, capacity=1)  # Radio Channel, Only one node can talk at a time

        self.protocol = protocol
        self.classifier = classifier

        if self.protocol == 'Disco':
            primes = Primes()
            # generate 11 primes, they are: [3, 5, 7, 11, 13, 17, 19, 23]
            # represents dutycycle range from 1/3 ~ 1/23
            self.primes = primes[1:9]

    def deploy_nodes(self):
        # add random nodes in region
        for nodeid in range(1, 101):
            random.seed(time.time() + random.random())
            dutycycle = random.randint(int(self.DUTYCYCLE_LOWER), int(self.DUTYCYCLE_UPPER))
            x = random.random() * 50  # x in [0, 50]
            y = random.random() * 50  # y in [0, 50]
            node = Node(self, str(nodeid), str(x), str(y), self.TRANS_POWER, dutycycle)
            self.nodes.append(node)


    def stop(self):
        raise Neighbor_discover_finished
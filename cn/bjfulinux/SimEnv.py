import random
import time
from cn.bjfulinux.Node import Node
import simpy
from cn.bjfulinux.Neigbhor_discover_finished import Neighbor_discover_finished



class SimEnv(simpy.Environment):
    def __init__(self, noise_thre):
        simpy.Environment.__init__(self)
        self.nodes = []
        self.NOISE_THRE = noise_thre

    def env_init(self, conf, classifier):
        self.TRANS_POWER = conf.get('topo', 'trans_power')
        self.MIN_RCV_RSSI = conf.get('topo', 'min_rcv_rssi')  # http://www.docin.com/p-266689616.html
        self.DUTYCYCLE_UPPER = conf.get('simulation', 'dutycycle_upper')
        self.DUTYCYCLE_LOWER = conf.get('simulation', 'dutycycle_lower')
        self.TIME_SLOT = round(float(conf.get('simulation', 'time_slot_milli')) / 1000, 3)

        self.wireless_channel = simpy.Resource(self, capacity=1)  # Radio Channel, Only one node can talk at a time

        self.classifier = classifier

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
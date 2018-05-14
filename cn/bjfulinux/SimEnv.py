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
            #primes = Primes()
            # generate 11 primes, they are: [3, 5, 7, 11, 13, 17, 19, 23]
            # represents dutycycle range from 1/3 ~ 1/23
            #self.primes = primes[1:9]
            self.primes = [[5, 11], [5, 13], [7, 13], [7,17], [11, 13], [11,17]]



    def deploy_nodes(self):
        # add random nodes in region
        # 产生100个互不相等在一定范围内的坐标集
        '''
        pos_set = set()
        while pos_set.__len__() < 101:
            random.seed(time.time() + random.random())
            x = str(random.randint(0, 50)) # from 0 to 50
            y = str(random.randint(0, 50))
            pos_set.add(x+'|'+y)
        pos_list = list(pos_set)'''
        pos_list = ['35|13', '28|10', '19|40', '30|12', '41|1', '32|34', '29|25', '0|40', '37|43', '37|40',
                    '35|1', '30|28', '26|10', '27|47', '4|8', '50|4', '23|50', '36|4', '6|24', '13|44',
                    '17|24', '49|38', '46|12', '49|7', '32|37', '2|7', '43|18', '29|50', '45|19', '10|14',
                    '2|34', '16|7', '10|40', '24|4', '11|33', '47|37', '3|43', '35|37', '42|35', '22|28',
                    '33|1', '1|20', '42|50', '19|20', '32|35', '16|40', '33|6', '37|7', '8|46', '10|38',
                    '19|29', '20|41', '40|14', '17|13', '35|26', '39|5', '14|17', '42|3', '30|49', '46|21',
                    '45|13', '37|38', '32|42', '24|22', '11|31', '12|47', '33|49', '9|32', '17|39', '46|17',
                    '40|10', '6|9', '18|28', '14|1', '0|37', '15|14', '10|12', '22|45', '24|36', '36|43',
                    '26|23', '48|22', '49|19', '2|21', '6|41', '48|7', '10|1', '6|42', '35|9', '48|47',
                    '38|14', '10|19', '49|30', '49|44', '2|48', '26|42', '8|48', '42|34', '27|39', '29|20', '21|43']
        for nodeid in range(1, 101):
            random.seed(time.time() + random.random())
            dutycycle = random.randint(int(self.DUTYCYCLE_LOWER), int(self.DUTYCYCLE_UPPER))
            x, y = pos_list[nodeid-1].split('|')
            node = Node(self, str(nodeid), x, y, self.TRANS_POWER, dutycycle)
            self.nodes.append(node)


    def stop(self):
        raise Neighbor_discover_finished
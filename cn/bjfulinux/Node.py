# -*- encoding: utf-8 -*-
from cn.bjfulinux.Message import Message
import random
import time
import math
from cn.bjfulinux.SignalMath import SignalMath
from cn.bjfulinux.NeighborMathTool import NeighborMathTool


class Node:
    def __init__(self, env, nodeid, x, y, power, dutycycle):
        # neighbor table:
        #  nodeid   rssi     nei_table_of_nei      nodeid  rssi
        #    |        |          |                     |    |
        # {'2':{rssi:-83.4, sub_neighbors:{'3':-50.3, '6':-61,...(邻居的邻居)...}, ...(其它邻居)...}
        self.neighbors = {}
        self.active = False
        self.nodeid, self.x, self.y, self.power, self.dutycycle = nodeid, int(x), int(y), power, dutycycle
        # print("%s node %s deployed at (%s, %s) with power %s, dutycycle: %s%%"
        #      % (env.now, nodeid, x, y, power, dutycycle))
        env.process(self.random_boot(env))

    def random_boot(self, env):
        random.seed(time.time() + random.random())
        self.boot_shift = float(random.randint(0, 1000)) / 1000.0
        yield env.timeout(self.boot_shift)
        # print("%s node %s booted" % (env.now, self.nodeid))
        self.active = True
        if env.protocol == 'Disco':
            env.process(self.start_dutycycle_disco(env))
        else:
            env.process(self.start_dutycycle(env))

    def proactive(self, env, delay):
        self.active = True
        yield env.timeout(env.TIME_SLOT) # active slot = 1
        self.active = False

    def start_dutycycle(self, env):
        while True:
            # send probe message both in the beginning and the end
            # to be compatible with unaligned slots
            self.active = True
            self.send_neighbor_probe(env)
            yield env.timeout(env.TIME_SLOT)  # active slot = 1
            self.send_neighbor_probe(env)
            # print("%s node %s sleep" % (env.now, self.nodeid))
            self.active = False
            yield env.timeout(1.0 / (self.dutycycle / 100) * env.TIME_SLOT)  # sleep slots = 1/dutycycle
            # print("%s node %s active" % (env.now, self.nodeid))

    def start_dutycycle_disco(self, env):
        # Disco protocol dutycycle
        self.prime = env.primes[int(8 * random.random())]
        i = 0
        while True:
            # send probe message both in the beginning and the end
            # to be compatible with unaligned slots
            if i == 0:
                self.active = True
                self.send_neighbor_probe(env)
                yield env.timeout(env.TIME_SLOT)
                self.send_neighbor_probe(env)
                self.active = False
            else:
                yield env.timeout(env.TIME_SLOT)
            i += 1
            if i == self.prime:
                i = 0

    def send_neighbor_probe(self, env):
        """
        :param env: environment
        :return: none
        Send neighbor discover message. Ignore message collision here.
        """
        """ ****ignore***
        with env.wireless_channel.request() as channel:
            yield channel
            print("%s node %s get the channel and send probe" % (env.now, self.nodeid))
            # create a radio event
            message = Message(self)
            message.should_receive(env)
        """
        #            print("%s node %s send probe" % (env.now, self.nodeid))
        # create a radio event
        message = Message(self)
        message.should_receive(env)

    def send_referring_msg(self, env, target, presentees):
        target.recvd_referring_msg(env, presentees)

    def neighbor_refer(self, env, message):
        if not self.neighbors.__len__():
            return
        if env.protocol == 'Naive' or env.protocol == 'Disco':
            return
        presentees = []
        for nodeid in self.neighbors:
            if nodeid == message.source_node.nodeid: # pass target
                continue
            if nodeid == self.nodeid: # pass self
                continue
            if nodeid in message.source_node.neighbors: # presentee already in target
                continue
            node = NeighborMathTool.get_node_by_id(env.nodes, nodeid)
            if env.protocol == 'Smart-ref':
                predict_data = NeighborMathTool.predict_data_prepare(self,
                                                                     node, message.source_node, env.NOISE_THRE,
                                                                     env.TRANS_POWER, env.MIN_RCV_RSSI)
                if not predict_data:
                    continue
                if env.classifier.predict(predict_data)[0]:
                    presentees.append(node)
            if env.protocol == 'Group-based':
                if NeighborMathTool.neighborhood_prob(self,node, message.source_node, env.NOISE_THRE,
                                                    env.TRANS_POWER, env.MIN_RCV_RSSI) >= 0.25:
                    presentees.append(node)
        if not presentees:
            self.send_referring_msg(env, message.source_node, presentees)


    def receive(self, env, message, rssi):
        if not self.active:
            return
        self.NEIGHBOR_ADDED = False
        if message.source_node.nodeid not in self.neighbors.keys():
            self.NEIGHBOR_ADDED = True
            NeighborMathTool.all_nodes_nei_num(env)
        self.neighbors[message.source_node.nodeid] = {}
        self.neighbors[message.source_node.nodeid]['rssi'] = rssi
        self.neighbors[message.source_node.nodeid]['sub_neighbors'] = {}
        for neighbor_id, other_info_dict in message.source_node.neighbors.items():
            self.neighbors[message.source_node.nodeid]['sub_neighbors'][neighbor_id] = other_info_dict['rssi']
        # print("%s node %s: " % (env.now, self.nodeid), self.neighbors)
        # print("%s node %s:%d" % (env.now, self.nodeid, self.neighbors.__len__()))
        if self.NEIGHBOR_ADDED:
            #print("%s node %s: " % (env.now, self.nodeid), self.neighbors)
            #print("%s node %s:%d" % (env.now, self.nodeid, self.neighbors.__len__()))
            #pass
            self.neighbor_refer(env, message)

    def recvd_referring_msg(self, env, presentees):
        for presentee in presentees:
            # 节点在presentee的sleep_slots+2*active_slot主动醒来就能保证和presentee重叠
            self.proactive(env, 1.0 / (presentee.dutycycle / 100) * env.TIME_SLOT + 2*env.TIME_SLOT)


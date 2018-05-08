# -*- encoding: utf-8 -*-
import uuid
from cn.bjfulinux.SignalMath import SignalMath



class Message:

    def __init__(self, node):
        self.uuid = uuid.uuid1()
        self.source_node = node

    def should_receive(self, env):
        for node in env.nodes:
            if node.nodeid == self.source_node.nodeid:
                continue
            else:
                rssi = SignalMath.cal_rssi(self.source_node, node, env.TRANS_POWER, env.NOISE_THRE)
                if rssi < float(env.MIN_RCV_RSSI):
                    continue  # can not receive the message
                else:  # receive
                    node.receive(env, self, rssi)
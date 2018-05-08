# -*- encoding: utf-8 -*-
from numpy import *
import math
import time


class SignalMath:
    @staticmethod
    def cal_rssi(node1, node2, trans_power, noise_thre=2):
        """
        :param noise_thre: noise threshold
        :param node1: node 1
        :param node2: node 2
        :param trans_power: transfer power, configured in config.ini
        :return: rssi value through distance
        ref: https://wenku.baidu.com/view/ce44b8c4d5bbfd0a7956738c.html
        RSSI simplified calculate
        """
        distance = SignalMath.cal_distance(node1, node2)
        if distance > 8:
            rssi = float(trans_power) - 58.5 - 10 * 3.3 * math.log10(distance)
        else:
            rssi = float(trans_power) - 40.2 - 10 * 2 * math.log10(distance)
        random.seed(int((time.time() % 10 + random.random()) * 100))
        random_noise = round(sqrt(noise_thre) * random.randn(), 2)  # 随机噪声上限
        return round(rssi - random_noise, 2)

    @staticmethod
    def resume_distance_from_rssi(rssi, trans_power):
        if rssi < (trans_power - 58.5 - 10 * 3.3 * math.log10(8)) + 5:
            d = 10 ** (-(rssi - trans_power + 58.5) / 33)
        else:
            d = 10 ** (-(rssi - trans_power + 40.2) / 20)
        return d

    @staticmethod
    def cal_distance(node1, node2):
        """
        :param node1: node 1
        :param node2: node 2
        :return: euclidean distance between of two nodes
        """
        return sqrt((float(node1.x) - float(node2.x)) ** 2 + (float(node1.y) - float(node2.y)) ** 2)

    @staticmethod
    def square_in_common_nei(trans_power, min_rssi, d):
        r = SignalMath.resume_distance_from_rssi(float(min_rssi), float(trans_power))
        alpha = math.acos((d ** 2) / (2 * r * d))
        return 2 * alpha * r ** 2 - r * d * math.sin(alpha)

    @staticmethod
    def func_square_d(x, s, r):
        d, alpha = x.tolist()
        return [
            (d ** 2) / (2 * r * d) - math.cos(alpha),
            2 * alpha * r ** 2 - r * d * math.sin(alpha) - s
        ]

    @staticmethod
    def solve_d_from_square(s, trans_power, r_str):
        r = SignalMath.resume_distance_from_rssi(float(r_str), float(trans_power))
        import scipy.optimize
        return scipy.optimize.fsolve(SignalMath.func_square_d, array([15, 1]), args=(s, r))[0]

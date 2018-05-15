import math
from numpy import array
from cn.bjfulinux.SignalMath import SignalMath
from functools import reduce
import simpy


class NeighborMathTool:

    @staticmethod
    def all_nodes_nei_num(env, final=False):
        all_neighbors = reduce(lambda x, y: x + y, [node.neighbors.__len__() for node in env.nodes])
        if final:
            print("INF", str(all_neighbors))
            return
        if all_neighbors>=1500:
            #print(round(env.now, 2), all_neighbors)
            env.stop()

    @staticmethod
    def common_neighbor_num(list1, list2, list3=None):
        if not list3:
            list3 = list2
        return list(set(list1) & set(list2) & set(list3)).__len__()

    @staticmethod
    def common_neighbor_rate(list1, list2, list3=None):
        """
        :param list1: neighbors of node 1
        :param list2: neighbors of node 2
        :param list3: neighbors of node 3
        :return: Common neighbor rate between node 1, 2 and 3
        e.g. node 1 has neighbors: 3 4 6, node 2 has neighbors 3 4 7 8,
        then common neighbor rate between node 1 and 2 are 2/5.
        """
        if not list3:
            list3 = list2
        return float(list(set(list1) & set(list2) & set(list3)).__len__()) / \
               float(list(set(list1) | set(list2) | set(list3)).__len__())

    @staticmethod
    def sigmoid(x):
        return 1.0 / (1 + math.exp(-x))

    @staticmethod
    def get_node_by_id(nodes, wanted_id):
        for seed_node in nodes:
            if seed_node.nodeid == wanted_id:
                return seed_node

    @staticmethod
    def can_hear_each_other(node1_str, node2_str, env):
        node1 = NeighborMathTool.get_node_by_id(env.nodes, node1_str)
        node2 = NeighborMathTool.get_node_by_id(env.nodes, node2_str)
        rssi = SignalMath.cal_rssi(node1, node2, env.TRANS_POWER)
        return 0 if rssi < float(env.MIN_RCV_RSSI) else 1

    @staticmethod
    def distance_in_rssi(rssi):
        """
        Describe distance from rssi side.
        :param rssi:
        :return:
        """
        d_rssi = float(NeighborMathTool.sigmoid(rssi / 10.0 + 5))
        return d_rssi

    @staticmethod
    def distance(node1, node2, common_neighbor_rate_value):
        """
        Novel metric to describe distance between node1 and node2.
        :param node1:
        :param node2:
        :param common_neighbor_rate_value:
        :return:
        """
        accumulate_dis = 0.0
        common_num = 0
        for nodei in node1:
            if nodei in node2.keys():
                common_num += 1
                accumulate_dis += NeighborMathTool.distance_in_rssi((node2[nodei] + node1[nodei]) / 2.0)
        if common_num == 0:
            return 0
        avg_dis = accumulate_dis / common_num
        return round(math.sqrt(avg_dis * common_neighbor_rate_value), 4)

    @staticmethod
    def sort_neighbors_by_rssi(node):
        neighbors_list = [node.neighbors[key]['rssi'] for key in node.neighbors]
        return sorted(neighbors_list, reverse=True)

    @staticmethod
    def predict_data_prepare(referer, presentee, target, noise_thre, trans_power, min_rssi):
        if presentee.nodeid not in referer.neighbors.keys():
            return
        # form neighbor list
        referer_neighbors = {}
        for nei_node_id in referer.neighbors.keys():
            referer_neighbors[nei_node_id] = referer.neighbors[nei_node_id]['rssi']
        presentee_neighbors = referer.neighbors[presentee.nodeid]['sub_neighbors']
        target_neighbors = referer.neighbors[target.nodeid]['sub_neighbors']
        referer_neighbors_list = list(referer.neighbors.keys())
        referer_neighbors_list.append(referer.nodeid)
        presentee_neighbors_list = list(presentee_neighbors.keys())
        presentee_neighbors_list.append(presentee.nodeid)
        target_neighbors_list = list(target_neighbors.keys())
        target_neighbors_list.append(target.nodeid)

        # common neighbor rate metrics
        common_neighbor_r_p = NeighborMathTool.common_neighbor_rate(referer_neighbors_list, presentee_neighbors_list)
        common_neighbor_r_t = NeighborMathTool.common_neighbor_rate(referer_neighbors_list, target_neighbors_list)
        common_neighbor_p_t = NeighborMathTool.common_neighbor_rate(presentee_neighbors_list, target_neighbors_list)
        if not (common_neighbor_p_t and common_neighbor_r_p and common_neighbor_r_t):
            return

        # distance metrics
        distance_r_p = NeighborMathTool.distance(referer_neighbors, presentee_neighbors, common_neighbor_r_p)
        distance_r_t = NeighborMathTool.distance(referer_neighbors, target_neighbors, common_neighbor_r_t)

        if not (distance_r_p and distance_r_t):
            return

        # common neighbor rate between RP and RT, i.e. common neighbors between RPT
        common_neighbor_rate_trilateral = NeighborMathTool.common_neighbor_rate(referer_neighbors_list,
                                                                                presentee_neighbors_list,
                                                                                target_neighbors_list)

        # calculate distance from rssi
        distance_from_rssi_r_p = SignalMath.resume_distance_from_rssi(referer_neighbors[presentee.nodeid],
                                                                      float(trans_power))
        distance_from_rssi_r_t = SignalMath.resume_distance_from_rssi(referer_neighbors[target.nodeid],
                                                                      float(trans_power))

        # rate between distance and common neighbor num
        k1 = SignalMath.square_in_common_nei(trans_power, min_rssi, distance_from_rssi_r_p) \
             / float(NeighborMathTool.common_neighbor_num(referer_neighbors_list, presentee_neighbors_list))
        k2 = SignalMath.square_in_common_nei(trans_power, min_rssi, distance_from_rssi_r_t) \
             / float(NeighborMathTool.common_neighbor_num(referer_neighbors_list, target_neighbors_list))

        # common square between P and T
        square = math.sqrt((k1 ** 2 + k2 ** 2) / 2) * common_neighbor_p_t

        # distance between p and t
        distance_p_t = SignalMath.solve_d_from_square(square, trans_power, min_rssi)

        # top n rssi of neighbors
        sorted_neighbors_of_presentee = NeighborMathTool.sort_neighbors_by_rssi(presentee)
        average_rssi_of_presentee = round(sum(sorted_neighbors_of_presentee.__iter__()) * 1.0 \
                                          / sorted_neighbors_of_presentee.__len__(), 2)

        return [distance_r_p, distance_r_t, round(distance_p_t, 4), referer_neighbors[presentee.nodeid],
                referer_neighbors[target.nodeid], round(common_neighbor_r_p, 4), round(common_neighbor_r_t, 4),
                round(common_neighbor_p_t, 4), round(common_neighbor_rate_trilateral, 4),
                sorted_neighbors_of_presentee[0], average_rssi_of_presentee, noise_thre]

    @staticmethod
    def n_vs_d_in_group_based_eqn_7(x, n, r, k):
        '''
        公式7 Group-based 论文
        '''
        l = x[0]
        return [
            n - k / (math.pi * r * r) * (2 * r * r * math.acos(l / (2 * r)) - l * math.sqrt(r * r - (l / 2) ** 2))
        ]

    @staticmethod
    def eqn_9_in_group_based(l1, l2, r):
        '''
        公式9 Group-based 论文
        '''
        if l1+l2 <= r:
            return 1
        else:
            cos_val = (l1**2+l2**2-r**2)/(2*l1*l2)
            if cos_val >= 1:
                return 0
            else:
                return 1/math.pi*math.acos(cos_val)

    @staticmethod
    def neighborhood_prob(referer, presentee, target, noise_thre, trans_power, min_rssi):
        if presentee.nodeid not in referer.neighbors.keys():
            return

        # form neighbor list
        referer_neighbors = {}
        for nei_node_id in referer.neighbors.keys():
            referer_neighbors[nei_node_id] = referer.neighbors[nei_node_id]['rssi']
        presentee_neighbors = referer.neighbors[presentee.nodeid]['sub_neighbors']
        target_neighbors = referer.neighbors[target.nodeid]['sub_neighbors']
        referer_neighbors_list = list(referer.neighbors.keys())
        referer_neighbors_list.append(referer.nodeid)
        presentee_neighbors_list = list(presentee_neighbors.keys())
        presentee_neighbors_list.append(presentee.nodeid)
        target_neighbors_list = list(target_neighbors.keys())
        target_neighbors_list.append(target.nodeid)

        # common neighbor rate metrics
        common_neighbor_r_p = NeighborMathTool.common_neighbor_num(referer_neighbors_list, presentee_neighbors_list)
        common_neighbor_r_t = NeighborMathTool.common_neighbor_num(referer_neighbors_list, target_neighbors_list)
        if not (common_neighbor_r_p and common_neighbor_r_t):
            return

        R = SignalMath.resume_distance_from_rssi(float(min_rssi) - float(noise_thre), float(trans_power))

        # density
        k = 50*50 / 100

        import scipy.optimize
        l_r_p = scipy.optimize.fsolve(NeighborMathTool.n_vs_d_in_group_based_eqn_7,
                                      array([20]), args=(common_neighbor_r_p, R, k))[0]
        l_r_t = scipy.optimize.fsolve(NeighborMathTool.n_vs_d_in_group_based_eqn_7,
                                      array([20]), args=(common_neighbor_r_t, R, k))[0]

        neighborhood_prob = NeighborMathTool.eqn_9_in_group_based(l_r_p, l_r_t, R)
        #print(neighborhood_prob)
        return neighborhood_prob

#!/usr/bin/env python
# coding=utf-8

import configparser
from cn.bjfulinux.Predictor import Predictor
from cn.bjfulinux.NeighborLogWR import NeighborLogWR
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

plt.style.use("ggplot")


protocols = ['Smart-ref', 'Group-based', 'Naive', 'Disco']
classifiers = ['xgb', 'svm', 'bayes']

# Read Config file: config.ini
conf = configparser.ConfigParser()
conf.read('./conf/config.ini')
sim_time = int(conf.get('simulation', 'single_run_time_seconds'))
times = int(conf.get('simulation', 'simulation_times'))
protocol = conf.get('protocol', 'protocol')
print("Uses protocol:",protocol,end="")
classifier = None
if protocol not in protocols:
    print("Invalid protocol! Supported:", protocols)
if protocol == 'Smart-ref':
    classifier_name = conf.get('protocol', 'classifier')
    if classifier_name not in classifiers:
        print("Invalid classifier! Supported:", classifiers)
    classifier = Predictor(classifier_name)
    print(" with classifier:",classifier_name,end="")


# ============   Display nodes ===================
# First set up the figure, the axis, and the plot element we want to animate
#fig = plt.figure()
#ax = plt.axes(xlim=(0, 50), ylim=(0, 50))
#line, = ax.plot([], [], lw=2)
# initialization function: plot the background of each frame
#nodes_pos_list = np.array([[int(node.x),int(node.y)] for node in env.nodes])
nodes_poses = [[35, 13], [28, 10], [19, 40], [30, 12], [41, 1], [32, 34], [29, 25], [0, 40], [37, 43], [37, 40],
                  [35, 1], [30, 28], [26, 10], [27, 47], [4, 8], [50, 4], [23, 50], [36, 4], [6, 24], [13, 44],
                  [17, 24], [49, 38], [46, 12], [49, 7], [32, 37], [2, 7], [43, 18], [29, 50], [45, 19], [10, 14],
                  [2, 34], [16, 7], [10, 40], [24, 4], [11, 33], [47, 37], [3, 43], [35, 37], [42, 35], [22, 28],
                  [33, 1], [1, 20], [42, 50], [19, 20], [32, 35], [16, 40], [33, 6], [37, 7], [8, 46], [10, 38],
                  [19, 29], [20, 41], [40, 14], [17, 13], [35, 26], [39, 5], [14, 17], [42, 3], [30, 49], [46, 21],
                  [45, 13], [37, 38], [32, 42], [24, 22], [11, 31], [12, 47], [33, 49], [9, 32], [17, 39], [46, 17],
                  [40, 10], [6, 9], [18, 28], [14, 1], [0, 37], [15, 14], [10, 12], [22, 45], [24, 36], [36, 43],
                  [26, 23], [48, 22], [49, 19], [2, 21], [6, 41], [48, 7], [10, 1], [6, 42], [35, 9], [48, 47],
                  [38, 14], [10, 19], [49, 30], [49, 44], [2, 48], [26, 42], [8, 48], [42, 34], [27, 39], [29, 20]]
nodes_pos_list = np.array(nodes_poses)
nodes_pos_x = list(nodes_pos_list[:, 0])
nodes_pos_y = list(nodes_pos_list[:, 1])

plt.ion()
plt.plot(nodes_pos_x, nodes_pos_y, 'o', color = 'b')
plt.title(protocol)
# ============ Draw line ================
log_reader = NeighborLogWR(protocol)
log_reader.openfile('r')
lines = log_reader.readlog()
log_reader.close()
logs = []
for oneline in lines:
    pos = oneline.split(' ')
    logs.append([float(pos[0]), int(pos[1]), int(pos[2]), int(pos[3]), int(pos[4])])
slot = 0.02
time = 1
line_num = 0
while line_num < lines.__len__():
    while line_num < lines.__len__() and time/20 >= logs[line_num][0]:
        plt.plot([logs[line_num][1], logs[line_num][3]], [logs[line_num][2], logs[line_num][4]], color='r', alpha=0.6)
        line_num += 1
    print('time: ' + str(time/20))
    plt.pause(slot)
    time += 1
plt.text(25, 30, str(time/20)+'s', size=50, style='oblique', ha='center',va='top',bbox=dict(boxstyle="round",ec=(1., 0.5, 0.5),fc=(1., 0.8, 0.8),))
# plt.ioff()
# plt.show()


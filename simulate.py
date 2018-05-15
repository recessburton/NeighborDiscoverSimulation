import configparser
from cn.bjfulinux.SimEnv import SimEnv
from cn.bjfulinux.Predictor import Predictor
from cn.bjfulinux.NeighborMathTool import NeighborMathTool
from cn.bjfulinux.Neigbhor_discover_finished import Neighbor_discover_finished
from cn.bjfulinux.NeighborLogWR import NeighborLogWR
import random
import simpy
from tqdm import tqdm


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


print('\nStart simulate ...',end='\n')

# Single Run
'''
noise_thre = round(2 * random.random(), 2)  # 随机噪声上限
env = SimEnv(noise_thre)
env.env_init(conf, protocol, classifier)
env.deploy_nodes()
try:
    env.run(until=sim_time)
    NeighborMathTool.all_nodes_nei_num(env, True)
except Neighbor_discover_finished as e:
    pass
env.nodes = []
del env
exit(0)
'''

# Muli-times
for i in tqdm(range(times), bar_format= "{l_bar} {bar} | {n_fmt}/{total_fmt}"):
    noise_thre = round(2 * random.random(), 2)  # 随机噪声上限
    env = SimEnv(noise_thre)
    env.env_init(conf, protocol, classifier)
    env.deploy_nodes()
    env.log_writer = NeighborLogWR(protocol)
    env.log_writer.openfile('a+')
    try:
        env.run(until=sim_time)
        NeighborMathTool.all_nodes_nei_num(env, True)
    except Neighbor_discover_finished as e:
        pass
    env.nodes = []
    del env
print("\nComplete.")

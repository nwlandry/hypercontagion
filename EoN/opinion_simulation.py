import random
import heapq
import numpy as np
import EoN
from collections import defaultdict
from collections import Counter

# canned functions
def degroot_model(members, status, epsilon):
    return("under dev")

def majority_rule(members, status, epsilon):
    return("under dev")

def voter_model(members, status, epsilon):
    return("under dev")

def deffuant_weisbuch(hyperedgeData, status, epsilon=0.5):
    status = status.copy()
    members = list(hyperedgeData["members"])
    d = 1/(len(members) - 1)*np.sum(np.power(status[members] - np.mean(status[members]), 2))
    if d < epsilon:
        status[members] = np.mean(status[members])
        return status
    else:
        return status

def hegselmann_krause_model(members, status, epsilon):
    return("under dev")

def random_group_sim_continuous_1D(G, initial_states, function=deffuant_weisbuch, tmin=0, tmax=100, return_full_data=False, dt=1, **args):
    time = tmin
    timesteps = int((tmax - tmin)/dt)+2
    states = np.empty((G.number_of_nodes(), timesteps))
    times = np.empty(timesteps)
    step = 0
    times[step] = time
    states[:, step] = initial_states.copy()
    while time <= tmax:
        time += dt
        step += 1
        # randomly select hyperedge
        uid = random.choice(list(G.hyperedges.keys()))
        states[:, step] = function(G.hyperedges[uid], states[:, step-1], **args)
        times[step] = time

    return times, states

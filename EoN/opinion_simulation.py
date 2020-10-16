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

def deffuant_weisbuch(hyperedgeData, status, epsilon=0.5, update="cautious", m=0.1):
    status = status.copy()
    members = list(hyperedgeData["members"])
    if discordance(members, status) < epsilon:
        if update == "average":
            status[members] = np.mean(status[members])
            return status
        elif update == "cautious":
            status[members] = status[members] + m*(np.mean(status[members]) - status[members])
            return status
    else:
        return status

def discordance(members, status):
    return 1/(len(members) - 1)*np.sum(np.power(status[members] - np.mean(status[members]), 2))

def hegselmann_krause(G, status, epsilon=0.01):
    newStatus = status.copy()
    for node in G.nodeLabels:
        newStatus[node] = 0
        for uid, nbr in G.neighbors[node].items():
            nodeNeighbors = list(nbr["neighbors"])
            if discordance(nodeNeighbors + [node], status) < epsilon:
                print(discordance(nodeNeighbors + [node], status))
                newStatus[node] += np.mean(status[nodeNeighbors])/len(G.neighbors[node])
    return newStatus

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

def synchronous_update_continuous_1D(G, initial_states, function=hegselmann_krause, tmin=0, tmax=100, return_full_data=False, dt=1, **args):
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
        states[:, step] = function(G, states[:, step-1], **args)
        times[step] = time

    return times, states

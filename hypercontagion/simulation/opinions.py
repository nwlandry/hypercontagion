import random
import heapq
import numpy as np
from collections import defaultdict
from collections import Counter

# built-in functions

# discrete output
def majority_rule(members, status):
    return "under dev"


def quorum(members, status, threshold=0.5):
    return "under dev"


def voter_model(node, edge, status, p_adoption=1):
    neighbors = [n for n in edge if n != node]
    opinions = set(status[neighbors])  # get unique opinions
    if len(opinions) == 1:
        if random.random() <= p_adoption:
            status[node] = opinions.pop()
    return status


# continuous output
def discordance(edge, status):
    try:
        return (
            1
            / (len(edge) - 1)
            * np.sum(np.power(status[edge] - np.mean(status[edge]), 2))
        )
    except ZeroDivisionError:
        return float("Inf")  # handles singleton edges


def deffuant_weisbuch(edge, status, epsilon=0.5, update="average", m=0.1):
    status = status.copy()
    if discordance(edge, status) < epsilon:
        if update == "average":
            status[edge] = np.mean(status[edge])
            return status
        elif update == "cautious":
            status[edge] = status[edge] + m * (np.mean(status[edge]) - status[edge])
            return status
    else:
        return status


def hegselmann_krause(H, status, epsilon=0.1):
    new_status = status.copy()
    for node in H.nodes:
        new_status[node] = 0
        numberOfLikeMinded = 0
        for edge_id in H.nodes.memberships(node):
            edge = H.edges.members(edge_id)
            if discordance(edge, status) < epsilon:
                new_status[node] += np.mean(status[edge])
                numberOfLikeMinded += 1
        try:
            new_status[node] *= 1.0 / numberOfLikeMinded
        except:
            new_status[node] = status[node]
    return new_status


def simulate_random_group_continuous_state_1D(
    H, initial_states, function=deffuant_weisbuch, tmin=0, tmax=100, dt=1, **args
):
    time = tmin
    timesteps = int((tmax - tmin) / dt) + 2
    states = np.empty((H.number_of_nodes(), timesteps))
    times = np.empty(timesteps)
    step = 0
    times[step] = time
    states[:, step] = initial_states.copy()
    while time <= tmax:
        time += dt
        step += 1
        # randomly select hyperedge
        edge = H.edges.members(random.choice(list(H.edges)))

        states[:, step] = function(edge, states[:, step - 1], **args)
        times[step] = time

    return times, states


def simulate_random_node_and_group_discrete_state(
    H, initial_states, function=voter_model, tmin=0, tmax=100, dt=1, **args
):
    time = tmin
    timesteps = int((tmax - tmin) / dt) + 2
    states = np.empty((H.number_of_nodes(), timesteps), dtype=object)
    times = np.empty(timesteps)
    step = 0
    times[step] = time
    states[:, step] = initial_states.copy()
    while time <= tmax:
        time += dt
        step += 1
        # randomly selct node
        node = random.choice(list(H.nodes))
        # randomly select neighbors of the node
        edge = H.edges.members(random.choice(list(H.edges)))

        states[:, step] = function(node, edge, states[:, step - 1], **args)
        times[step] = time

    return times, states


def synchronous_update_continuous_state_1D(
    H, initial_states, function=hegselmann_krause, tmin=0, tmax=100, dt=1, **args
):
    time = tmin
    timesteps = int((tmax - tmin) / dt) + 2
    states = np.empty((H.number_of_nodes(), timesteps))
    times = np.empty(timesteps)
    step = 0
    times[step] = time
    states[:, step] = initial_states.copy()
    while time <= tmax:
        time += dt
        step += 1
        states[:, step] = function(H, states[:, step - 1], **args)
        times[step] = time

    return times, states

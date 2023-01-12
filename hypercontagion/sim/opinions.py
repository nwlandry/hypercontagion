"""
Opinion formation models on hypergraphs.
"""

import random

import numpy as np


# built-in functions
def voter_model(node, edge, status, p_adoption=1):
    """the voter model given a hyperedge

    Parameters
    ----------
    node : hashable
        node whose opinion may change
    edge : iterable
        a list of the members of a hyperedge. must include the node.
    status : dict
        keys are node IDs, statuses are values
    p_adoption : float, default: 1
        probability that the node will adopt the consensus.

    Returns
    -------
    str
        new node status
    """
    neighbors = [n for n in edge if n != node]
    opinions = set(status[neighbors])  # get unique opinions
    if len(opinions) == 1:
        if random.random() <= p_adoption:
            status[node] = opinions.pop()
    return status


# continuous output
def discordance(edge, status):
    """Computes the discordance of a hyperedge.

    Parameters
    ----------
    edge : tuple
        a list of an edge's members
    status : numpy array
        opinions of the nodes

    Returns
    -------
    float
        discordance of the hyperedge
    """
    try:
        e = list(edge)
        return 1 / (len(e) - 1) * np.sum(np.power(status[e] - np.mean(status[e]), 2))
    except ZeroDivisionError:
        return float("Inf")  # handles singleton edges


def deffuant_weisbuch(edge, status, epsilon=0.5, update="average", m=0.1):
    """the deffuant weisbuch model for updating the statuses of nodes in an edge

    Parameters
    ----------
    edge : iterable
        list of nodes
    status : numpy array
        node statuses
    epsilon : float, default
        confidence bound
    update : str, default: "average"
        if "average" the opinions of all nodes in the hyperedge
        are updated to the average. If "cautious", the nodes are
        moved toward the average.

    m : float between 0 and 1, default: 0.1
        the fraction of the possible distance to move the node opinions
        to the centroid.

    Returns
    -------
    iterable
        the updated statuses
    """
    status = status.copy()
    e = list(edge)
    if discordance(e, status) < epsilon:
        if update == "average":
            status[e] = np.mean(status[e])
            return status
        elif update == "cautious":
            status[e] = status[e] + m * (np.mean(status[e]) - status[e])
            return status
    else:
        return status


def hegselmann_krause(H, status, epsilon=0.1):
    """The Hegselmann-Krause model.

    Parameters
    ----------
    H : xgi.Hypergraph
        the hypergraph of interest
    status : iterable
        statuses of the nodes.
    epsilon : float, default: 0.1
        confidence bound

    Returns
    -------
    iterable
        new opinions
    """

    members = H.edges.members(dtype=dict)
    memberships = H.nodes.memberships()

    new_status = status.copy()
    for node in H.nodes:
        new_status[node] = 0
        numberOfLikeMinded = 0
        for edge_id in memberships[node]:
            edge = list(members[edge_id])
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
    """Simulate an opinion formation process where states are continuous and
    random groups are chosen.

    Parameters
    ----------
    H : xgi.Hypergraph
        the hypergraph of interest
    initial_states : numpy array
        initial node states
    function : update function, default: deffuant_weisbuch
        node update function
    tmin : int, default: 0
        the time at which the simulation starts
    tmax : int, default: 100
        the time at which the simulation terminates
    dt : float > 0, default: 1
        the time step to take.

    Returns
    -------
    numpy array, numpy array
        a 1D array of the times and a 2D array of the states.
    """
    members = H.edges.members(dtype=dict)

    time = tmin
    timesteps = int((tmax - tmin) / dt) + 2
    states = np.empty((H.num_nodes, timesteps))
    times = np.empty(timesteps)
    step = 0
    times[step] = time
    states[:, step] = initial_states.copy()
    while time <= tmax:
        time += dt
        step += 1
        # randomly select hyperedge
        edge = members[random.choice(list(members))]

        states[:, step] = function(edge, states[:, step - 1], **args)
        times[step] = time

    return times, states


def simulate_random_node_and_group_discrete_state(
    H, initial_states, function=voter_model, tmin=0, tmax=100, dt=1, **args
):
    """Simulate an opinion formation process where states are discrete and
    states are updated synchronously.

    Parameters
    ----------
    H : xgi.Hypergraph
        the hypergraph of interest
    initial_states : numpy array
        initial node states
    function : update function, default: deffuant_weisbuch
        node update function
    tmin : int, default: 0
        the time at which the simulation starts
    tmax : int, default: 100
        the time at which the simulation terminates
    dt : float > 0, default: 1
        the time step to take.

    Returns
    -------
    numpy array, numpy array
        a 1D array of the times and a 2D array of the states.
    """
    members = H.edges.members(dtype=dict)
    time = tmin
    timesteps = int((tmax - tmin) / dt) + 2
    states = np.empty((H.num_nodes, timesteps), dtype=object)
    times = np.empty(timesteps)
    step = 0
    times[step] = time
    states[:, step] = initial_states.copy()
    while time <= tmax:
        time += dt
        step += 1
        # randomly select node
        node = random.choice(list(H.nodes))
        # randomly select neighbors of the node
        edge = members[random.choice(list(members))]

        states[:, step] = function(node, edge, states[:, step - 1], **args)
        times[step] = time

    return times, states


def synchronous_update_continuous_state_1D(
    H, initial_states, function=hegselmann_krause, tmin=0, tmax=100, dt=1, **args
):
    """Simulate an opinion formation process where states are continuous and
    states are updated synchronously.

    Parameters
    ----------
    H : xgi.Hypergraph
        the hypergraph of interest
    initial_states : numpy array
        initial node states
    function : update function, default: deffuant_weisbuch
        node update function
    tmin : int, default: 0
        the time at which the simulation starts
    tmax : int, default: 100
        the time at which the simulation terminates
    dt : float > 0, default: 1
        the time step to take.

    Returns
    -------
    numpy array, numpy array
        a 1D array of the times and a 2D array of the states.
    """
    time = tmin
    timesteps = int((tmax - tmin) / dt) + 2
    states = np.empty((H.num_nodes, timesteps))
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

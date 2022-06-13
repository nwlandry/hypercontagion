"""
Provides predefined contagion functions for use in the hypercontagion library.
"""

import random


# built-in functions
def collective_contagion(node, status, edge):
    """Collective contagion function.

    Parameters
    ----------
    node : hashable
        node ID
    status : dict
        keys are node IDs and values are their statuses.
    edge : iterable
        hyperedge

    Returns
    -------
    int
        0 if no transmission can occur, 1 if it can.
    """
    for i in set(edge).difference({node}):
        if status[i] != "I":
            return 0
    return 1


def individual_contagion(node, status, edge):
    """Individual contagion function.

    Parameters
    ----------
    node : hashable
        node ID
    status : dict
        keys are node IDs and values are their statuses.
    edge : iterable
        hyperedge

    Returns
    -------
    int
        0 if no transmission can occur, 1 if it can.
    """
    for i in set(edge).difference({node}):
        if status[i] == "I":
            return 1
    return 0


def threshold(node, status, edge, threshold=0.5):
    """Threshold contagion process.

    Contagion may spread if greater than a specified fraction
    of hyperedge neighbors are infected.

    Parameters
    ----------
    node : hashable
        node ID
    status : dict
        keys are node IDs and values are their statuses.
    edge : iterable of hashables
        nodes in the hyperedge
    threshold : float, default: 0.5
        the critical fraction of hyperedge neighbors above
        which contagion spreads.

    Returns
    -------
    int
        0 if no transmission can occur, 1 if it can.
    """
    neighbors = set(edge).difference({node})
    try:
        c = sum([status[i] == "I" for i in neighbors]) / len(neighbors)
    except:
        c = 0

    if c < threshold:
        return 0
    elif c >= threshold:
        return 1


def majority_vote(node, status, edge):
    """Majority vote contagion process.

    Contagion may spread if the majority of a node's
    hyperedge neighbors are infected. If it's a tie,
    the result is random.

    Parameters
    ----------
    node : hashable
        node ID
    status : dict
        keys are node IDs and values are their statuses.
    edge : iterable of hashables
        nodes in the hyperedge

    Returns
    -------
    int
        0 if no transmission can occur, 1 if it can.
    """
    neighbors = set(edge).difference({node})
    try:
        c = sum([status[i] == "I" for i in neighbors]) / len(neighbors)
    except:
        c = 0
    if c < 0.5:
        return 0
    elif c > 0.5:
        return 1
    else:
        return random.choice([0, 1])


def size_dependent(node, status, edge):

    return sum([status[i] == "I" for i in set(edge).difference({node})])

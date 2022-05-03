import random


# built-in functions
def collective_contagion(node, status, edge):
    """Collective contagion function.

    Parameters
    ----------
    node : hashable
        node ID
    status : dict
        keys are node IDs and values are the status.
    edge : iterable
        hyperedge

    Returns
    -------
    0 or 1
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
        keys are node IDs and values are the status.
    edge : iterable
        hyperedge

    Returns
    -------
    0 or 1
        0 if no transmission can occur, 1 if it can.
    """
    for i in set(edge).difference({node}):
        if status[i] == "I":
            return 1
    return 0


def threshold(node, status, edge, threshold=0.5):
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

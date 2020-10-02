import random
import heapq
import numpy as np
import EoN
from collections import defaultdict
from collections import Counter


def continuous_opinion(G, rate_function, transition_choice, initialCondition, return_statuses, rate_function, **args, tmin = 0, tmax=100, parameters = None, return_full_data = False, sim_kwargs = None):

    r'''
    Initially intended for a complex contagion.  However, this can allow influence
    from any nodes, not just immediate neighbors.

    The complex contagion must be something that all nodes do something simultaneously

    **This is not the same as if node** ``v`` **primes node** ``u`` **and
    later node** ``w`` **causes** ``u`` **to transition.  This will require
    that both** ``v`` **and** ``w`` **have the relevant states at the moment**
    **of transition and it has forgotten any previous history.**

    :Arguments:

    **G** (NetworkX Graph)
        The underlying network

    **rate_function**
        A function that will take the network, a node, and the statuses of all
        the nodes and calculate the rate at which the node changes its status.

        The function is called like

        if parameters is None:
            rate_function(G, node, status)
        else:
            rate_function(G, node, status, parameters)

        where G is the graph, node is the node, status is a dict such that
        status[u] returns the status of u, and parameters is the parameters
        passed to the function.

        it returns a number, the combined rate at which ``node`` might change
        status.


    **transition_choice**
        A function that takes the network, a node, and the statuses of all the
        nodes and chooses which event will happen.  The function should be
        called [with or without ``parameters``]

        if ``parameters`` is ``None``:
            ``transition_choice(G, node, status)``
        else:
            ``transition_choice(G, node, status, parameters)``

        where ``G`` is the graph, ``node` is the node, ``status` is a dict
        such that ``status[u]`` returns the status of u, and ``parameters`` is
        the parameters passed to the function.

        It should return the new status of ``node`` based on the fact that the
        node is changing status.

    **get_influence_set**
        When a node ``u`` changes status, we want to know which nodes may have their
        rate altered.  We need to update their rates.  This function returns all
        nodes that may be affected by ``u`` (either in its previous state or its
        current state).  We will go through and recalculate the rates for all
        of these nodes.  For a contagion, we can simply choose all neighbors,
        but it may be faster to leave out any nodes that it wouldn't have
        affected before or after its transition (e.g., R or I neighbors in SIR).

        if ``parameters`` is None:
            ``get_influence_set(G, node, status)``
        else:
            ``get_influence_set(G, node, status, parameters)``

        where G is the graph, node is the node, status is a dict such that
        status[u] returns the status of u, and parameters is the parameters
        passed to the function.

        it should return the set of nodes whose rates need to be recalculated.

        Most likely, it is

        def get_influence_set(G, node, status):
            return G.neighbors(node)


    **IC**
        A dict.  IC[node] returns the status of node.

    **return_statuses** list or other iterable (but not a generator)
        The statuses that we will return information for, in the order
        we will return them.

    **tmin** number (default 0)
        starting time

    **tmax** number (default 100)
        stop time

    **return_full_data** boolean
        currently needs to be False.  True raises an error.

    **parameters**  list/tuple.
        Any parameters of the functions rate_function, transition_choice, influence_set
        We assume all three functions can accept parameters.
        Examples: recovery rate, transmission rate, ...


    :Returns:

    **(times, status1, status2, ...)**  tuple of numpy arrays
        first entry is the times at which events happen.
        second (etc) entry is an array with the same number of entries as ``times``
        giving the number of nodes of status ordered as they are in ``return_statuses``


    :SAMPLE USE:
    This simply does an SIR epidemic, by saying that the rate of becoming
    infected is tau times the number of infected neighbors.


    ::


        import networkx as nx
        import EoN
        import matplotlib.pyplot as plt
        from collections import defaultdict #makes defining the initial condition easier


        def rate_function(G, node, status, parameters):
            #This function needs to return the rate at which node changes status.
            #
            tau,gamma = parameters
            if status[node] == 'I':
                return gamma
            elif status[node] == 'S':
                return tau*len([nbr for nbr in G.neighbors(node) if status[nbr] == 'I'])
            else:
                return 0

        def transition_choice(G, node, status, parameters):
            #this function needs to return the new status of node.  We already
            #know it is changing status.
            #
            #this function could be more elaborate if there were different
            #possible transitions that could happen.
            if status[node] == 'I':
                return 'R'
            elif status[node] == 'S':
                return 'I'

        def get_influence_set(G, node, status, parameters):
            #this function needs to return any node whose rates might change
            #because ``node`` has just changed status.
            #
            #the only neighbors a node might affect are the susceptible ones.

            return {nbr for nbr in G.neighbors(node) if status[nbr] == 'S'}

        G = nx.fast_gnp_random_graph(100000,0.00005)

        gamma = 1.
        tau = 0.5
        parameters = (tau, gamma)

        IC = defaultdict(lambda: 'S')
        for node in range(200):
            IC[node] = 'I'

        t, S, I, R = EoN.Gillespie_complex_contagion(G, rate_function,
                                   transition_choice, get_influence_set, IC,
                                   return_statuses=('S', 'I', 'R'),
                                   parameters=parameters)

        plt.plot(t, I)

    '''

    if parameters is None:
        parameters = ()


    status = {node: initialCondition[node] for node in G.nodes()} # each state is in R^n

    if return_full_data:
        node_history = {node:([tmin], [status[node]]) for node in G.nodes()}

    times = [tmin]
    t = tmin
    data = {}
    C = Counter(status.values())
    for return_status in return_statuses:
        data[return_status] = [C[return_status]]

    nodes_by_rate = _ListDict_(weighted=True)

    for u in G.nodes():
        rate = rate_function(G, u, status, parameters)
        if rate>0:
            nodes_by_rate.insert(u, weight = rate)

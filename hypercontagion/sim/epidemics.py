"""
Classic epidemiological models extended to higher-order contagion.
"""

import random
from collections import defaultdict

import numpy as np
import xgi

from ..exception import HyperContagionError
from ..utils import EventQueue, SamplingDict, _process_trans_SIR_, _process_trans_SIS_
from .functions import majority_vote, threshold


def discrete_SIR(
    H,
    tau,
    gamma,
    transmission_function=threshold,
    initial_infecteds=None,
    initial_recovereds=None,
    recovery_weight=None,
    transmission_weight=None,
    rho=None,
    tmin=0,
    tmax=float("Inf"),
    dt=1.0,
    return_event_data=False,
    seed=None,
    **args
):
    """Simulates the discrete SIR model for hypergraphs.

    Parameters
    ----------
    H : xgi.Hypergraph
        The hypergraph on which to simulate the SIR contagion process
    tau : dict
        Keys are edge sizes and values are transmission rates
    gamma : float
        Healing rate
    transmission_function : lambda function, default: threshold
        The contagion function that determines whether transmission is possible.
    initial_infecteds : iterable, default: None
        Initially infected node IDs.
    initial_recovereds : iterable, default: None
        Initially recovered node IDs.
    recovery_weight : hashable, default: None
        Hypergraph node attribute that weights the healing rate.
    transmission_weight : hashable, default: None
        Hypergraph edge attribute that weights the transmission rate.
    rho : float, default: None
        Fraction initially infected. Cannot be specified if
        `initial_infecteds` is defined.
    tmin : float, default: 0
        Time at which the simulation starts.
    tmax : float, default: float("Inf")
        Time at which the simulation terminates if there are still
        infected nodes.
    dt : float, default: 1.0
        The time step of the simulation.
    return_event_data : bool, default: False
        Whether to track each individual transition event that occurs.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.

    Returns
    -------
    tuple of np.arrays
        t, S, I, R

    Raises
    ------
    HyperContagionError
        If the user specifies both rho and initial_infecteds.
    """
    if seed is not None:
        random.seed(seed)
    members = H.edges.members(dtype=dict)
    memberships = H.nodes.memberships()

    if rho is not None and initial_infecteds is not None:
        raise HyperContagionError("cannot define both initial_infecteds and rho")

    if return_event_data:
        events = list()

    if initial_infecteds is None:
        if rho is None:
            initial_number = 1
        else:
            initial_number = int(round(H.num_nodes * rho))
        initial_infecteds = random.sample(list(H.nodes), initial_number)

    if initial_recovereds is None:
        initial_recovereds = []

    if transmission_weight is not None:

        def edgeweight(item):
            return item[transmission_weight]

    else:

        def edgeweight(item):
            return 1

    if recovery_weight is not None:

        def nodeweight(u):
            return H.nodes[u][recovery_weight]

    else:

        def nodeweight(u):
            return 1

    status = defaultdict(lambda: "S")
    for node in initial_infecteds:
        status[node] = "I"

        if return_event_data:
            events.append(
                {
                    "time": tmin,
                    "source": None,
                    "target": node,
                    "old_state": "S",
                    "new_state": "I",
                }
            )

    for node in initial_recovereds:
        status[node] = "R"

        if return_event_data:
            events.append(
                {
                    "time": tmin,
                    "source": None,
                    "target": node,
                    "old_state": "I",
                    "new_state": "R",
                }
            )

    if return_event_data:
        for node in (
            set(H.nodes).difference(initial_infecteds).difference(initial_recovereds)
        ):
            events.append(
                {
                    "time": tmin,
                    "source": None,
                    "target": node,
                    "old_state": None,
                    "new_state": "S",
                }
            )

    I = [len(initial_infecteds)]
    R = [len(initial_recovereds)]
    S = [H.num_nodes - I[0] - R[0]]
    times = [tmin]
    t = tmin

    new_status = status

    while t <= tmax and I[-1] != 0:
        S.append(S[-1])
        I.append(I[-1])
        R.append(R[-1])

        for node in H.nodes:
            if status[node] == "I":
                # heal
                if random.random() <= gamma * dt * nodeweight(node):
                    new_status[node] = "R"
                    R[-1] += 1
                    I[-1] += -1

                    if return_event_data:
                        events.append(
                            {
                                "time": t,
                                "source": None,
                                "target": node,
                                "old_state": "I",
                                "new_state": "R",
                            }
                        )
                else:
                    new_status[node] = "I"
            elif status[node] == "S":
                # infect by neighbors of all sizes
                for edge_id in memberships[node]:
                    edge = members[edge_id]
                    if tau[len(edge)] > 0:
                        if random.random() <= tau[len(edge)] * transmission_function(
                            node, status, edge, **args
                        ) * dt * edgeweight(edge_id):
                            new_status[node] = "I"
                            S[-1] += -1
                            I[-1] += 1

                            if return_event_data:
                                events.append(
                                    {
                                        "time": t,
                                        "source": edge_id,
                                        "target": node,
                                        "old_state": "S",
                                        "new_state": "I",
                                    }
                                )
                            break
                else:
                    new_status[node] == "S"
        status = new_status.copy()
        t += dt
        times.append(t)
    if return_event_data:
        return events
    else:
        return np.array(times), np.array(S), np.array(I), np.array(R)


def discrete_SIS(
    H,
    tau,
    gamma,
    transmission_function=threshold,
    initial_infecteds=None,
    recovery_weight=None,
    transmission_weight=None,
    rho=None,
    tmin=0,
    tmax=float("Inf"),
    dt=1.0,
    return_event_data=False,
    seed=None,
    **args
):
    """Simulates the discrete SIS model for hypergraphs.

    Parameters
    ----------
    H : xgi.Hypergraph
        The hypergraph on which to simulate the SIR contagion process
    tau : dict
        Keys are edge sizes and values are transmission rates
    gamma : float
        Healing rate
    transmission_function : lambda function, default: threshold
        The contagion function that determines whether transmission is possible.
    initial_infecteds : iterable, default: None
        Initially infected node IDs.
    initial_recovereds : iterable, default: None
        Initially recovered node IDs.
    recovery_weight : hashable, default: None
        Hypergraph node attribute that weights the healing rate.
    transmission_weight : hashable, default: None
        Hypergraph edge attribute that weights the transmission rate.
    rho : float, default: None
        Fraction initially infected. Cannot be specified if
        `initial_infecteds` is defined.
    tmin : float, default: 0
        Time at which the simulation starts.
    tmax : float, default: float("Inf")
        Time at which the simulation terminates if there are still
        infected nodes.
    dt : float, default: 1.0
        The time step of the simulation.
    return_event_data : bool, default: False
        Whether to track each individual transition event that occurs.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.

    Returns
    -------
    tuple of np.arrays
        t, S, I

    Raises
    ------
    HyperContagionError
        If the user specifies both rho and initial_infecteds.
    """

    if seed is not None:
        random.seed(seed)

    members = H.edges.members(dtype=dict)
    memberships = H.nodes.memberships()

    if rho is not None and initial_infecteds is not None:
        raise HyperContagionError("cannot define both initial_infecteds and rho")

    if return_event_data:
        events = list()

    if initial_infecteds is None:
        if rho is None:
            initial_number = 1
        else:
            initial_number = int(round(H.num_nodes * rho))
        initial_infecteds = random.sample(list(H.nodes), initial_number)

    if transmission_weight is not None:

        def edgeweight(item):
            return item[transmission_weight]

    else:

        def edgeweight(item):
            return 1

    if recovery_weight is not None:

        def nodeweight(u):
            return H.nodes[u][recovery_weight]

    else:

        def nodeweight(u):
            return 1

    status = defaultdict(lambda: "S")
    for node in initial_infecteds:
        status[node] = "I"

        if return_event_data:
            events.append(
                {
                    "time": tmin,
                    "source": None,
                    "target": node,
                    "old_state": "S",
                    "new_state": "I",
                }
            )

    if return_event_data:
        for node in set(H.nodes).difference(initial_infecteds):
            events.append(
                {
                    "time": tmin,
                    "source": None,
                    "target": node,
                    "old_state": "I",
                    "new_state": "S",
                }
            )

    I = [len(initial_infecteds)]
    S = [H.num_nodes - I[0]]
    times = [tmin]
    t = tmin
    new_status = status

    while t <= tmax and I[-1] != 0:
        S.append(S[-1])
        I.append(I[-1])

        for node in H.nodes:
            if status[node] == "I":
                # heal
                if random.random() <= gamma * dt * nodeweight(node):
                    new_status[node] = "S"
                    S[-1] += 1
                    I[-1] += -1

                    if return_event_data:
                        events.append(
                            {
                                "time": t,
                                "source": None,
                                "target": node,
                                "old_state": "I",
                                "new_state": "S",
                            }
                        )
                else:
                    new_status[node] = "I"
            else:
                # infect by neighbors of all sizes
                for edge_id in memberships[node]:
                    edge = members[edge_id]
                    if tau[len(edge)] > 0:
                        if random.random() <= tau[len(edge)] * transmission_function(
                            node, status, edge, **args
                        ) * dt * edgeweight(edge_id):
                            new_status[node] = "I"
                            S[-1] += -1
                            I[-1] += 1

                            if return_event_data:
                                events.append(
                                    {
                                        "time": t,
                                        "source": edge_id,
                                        "target": node,
                                        "old_state": "S",
                                        "new_state": "I",
                                    }
                                )
                            break
                else:
                    new_status[node] == "S"
        status = new_status.copy()
        t += dt
        times.append(t)
    if return_event_data:
        return events
    else:
        return np.array(times), np.array(S), np.array(I)


def Gillespie_SIR(
    H,
    tau,
    gamma,
    transmission_function=threshold,
    initial_infecteds=None,
    initial_recovereds=None,
    rho=None,
    tmin=0,
    tmax=float("Inf"),
    recovery_weight=None,
    transmission_weight=None,
    return_event_data=False,
    seed=None,
    **args
):
    """Simulates the SIR model for hypergraphs with the Gillespie algorithm.

    Parameters
    ----------
    H : xgi.Hypergraph
        The hypergraph on which to simulate the SIR contagion process
    tau : dict
        Keys are edge sizes and values are transmission rates
    gamma : float
        Healing rate
    transmission_function : lambda function, default: threshold
        The contagion function that determines whether transmission is possible.
    initial_infecteds : iterable, default: None
        Initially infected node IDs.
    initial_recovereds : iterable, default: None
        Initially recovered node IDs.
    recovery_weight : hashable, default: None
        Hypergraph node attribute that weights the healing rate.
    transmission_weight : hashable, default: None
        Hypergraph edge attribute that weights the transmission rate.
    rho : float, default: None
        Fraction initially infected. Cannot be specified if
        `initial_infecteds` is defined.
    tmin : float, default: 0
        Time at which the simulation starts.
    tmax : float, default: float("Inf")
        Time at which the simulation terminates if there are still
        infected nodes.
    return_event_data : bool, default: False
        Whether to track each individual transition event that occurs.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.

    Returns
    -------
    tuple of np.arrays
        t, S, I, R

    Raises
    ------
    HyperContagionError
        If the user specifies both rho and initial_infecteds.
    """
    if seed is not None:
        random.seed(seed)

    members = H.edges.members(dtype=dict)
    memberships = H.nodes.memberships()

    if rho is not None and initial_infecteds is not None:
        raise HyperContagionError("cannot define both initial_infecteds and rho")

    if return_event_data:
        events = list()

    if transmission_weight is not None:

        def edgeweight(item):
            return item[transmission_weight]

    else:

        def edgeweight(item):
            return None

    if recovery_weight is not None:

        def nodeweight(u):
            return H.nodes[u][recovery_weight]

    else:

        def nodeweight(u):
            return None

    if initial_infecteds is None:
        if rho is None:
            initial_number = 1
        else:
            initial_number = int(round(H.num_nodes * rho))
        initial_infecteds = random.sample(list(H.nodes), initial_number)

    if initial_recovereds is None:
        initial_recovereds = []

    I = [len(initial_infecteds)]
    R = [len(initial_recovereds)]
    S = [H.num_nodes - I[0] - R[0]]
    times = [tmin]

    t = tmin

    status = defaultdict(lambda: "S")
    for node in initial_infecteds:
        status[node] = "I"

        if return_event_data:
            events.append(
                {
                    "time": tmin,
                    "source": None,
                    "target": node,
                    "old_state": "S",
                    "new_state": "I",
                }
            )

    for node in initial_recovereds:
        status[node] = "R"

        if return_event_data:
            events.append(
                {
                    "time": tmin,
                    "source": None,
                    "target": node,
                    "old_state": "I",
                    "new_state": "R",
                }
            )

    if return_event_data:
        for node in (
            set(H.nodes).difference(initial_infecteds).difference(initial_recovereds)
        ):
            events.append(
                {
                    "time": tmin,
                    "source": None,
                    "target": node,
                    "old_state": None,
                    "new_state": "S",
                }
            )

    if recovery_weight is None:
        infecteds = SamplingDict()
    else:
        infecteds = SamplingDict(weighted=True)

    unique_edge_sizes = xgi.unique_edge_sizes(H)
    IS_links = dict()
    for size in unique_edge_sizes:
        if transmission_weight is None:
            IS_links[size] = SamplingDict()
        else:
            IS_links[size] = SamplingDict(weighted=True)

    for node in initial_infecteds:
        infecteds.update(node, weight_increment=nodeweight(node))
        for edge_id in memberships[node]:
            edge = members[edge_id]
            for nbr in edge:
                if status[nbr] == "S":
                    contagion = transmission_function(nbr, status, edge, **args)
                    if contagion != 0:
                        IS_links[len(edge)].update(
                            (edge_id, nbr),
                            weight_increment=edgeweight(edge_id),
                        )  # need to be able to multiply by the contagion?

    total_rates = dict()
    total_rates[0] = gamma * infecteds.total_weight()  # I_weight_sum
    for size in unique_edge_sizes:
        total_rates[size] = tau[size] * IS_links[size].total_weight()  # IS_weight_sum

    total_rate = sum(total_rates.values())

    if total_rate > 0:
        delay = random.expovariate(total_rate)
    else:
        print("Total rate is zero and no events will happen!")
        delay = float("Inf")

    t += delay

    while infecteds and t < tmax:
        while True:
            choice = random.choice(
                list(total_rates.keys())
            )  # Is there a faster way to do this?
            if random.random() < total_rates[choice] / total_rate:
                break
        if choice == 0:  # recover
            # does weighted choice and removes it
            recovering_node = infecteds.random_removal()
            status[recovering_node] = "R"

            if return_event_data:
                events.append(
                    {
                        "time": t,
                        "source": None,
                        "target": recovering_node,
                        "old_state": "I",
                        "new_state": "R",
                    }
                )

            for edge_id in memberships[recovering_node]:
                edge = members[edge_id]
                for nbr in edge:
                    if status[nbr] == "S" and (edge_id, nbr) in IS_links[len(edge)]:
                        contagion = transmission_function(nbr, status, edge, **args)
                        if contagion == 0:
                            try:
                                IS_links[len(edge)].remove((edge_id, nbr))
                            except:
                                pass

            times.append(t)
            S.append(S[-1])
            I.append(I[-1] - 1)
            R.append(R[-1] + 1)
        else:  # transmit
            source, recipient = IS_links[
                choice
            ].choose_random()  # we don't use remove since that complicates the later removal of edges.
            status[recipient] = "I"

            infecteds.update(recipient, weight_increment=nodeweight(recipient))

            if return_event_data:
                events.append(
                    {
                        "time": t,
                        "source": source,
                        "target": recipient,
                        "old_state": "S",
                        "new_state": "I",
                    }
                )

            for edge_id in memberships[recipient]:
                try:
                    IS_links[len(members[edge_id])].remove((edge_id, recipient))
                except:
                    pass

            for edge_id in memberships[recipient]:
                edge = members[edge_id]
                for nbr in edge:
                    if status[nbr] == "S":
                        contagion = transmission_function(nbr, status, edge, **args)
                        if contagion != 0:
                            IS_links[len(edge)].update(
                                (edge_id, nbr),
                                weight_increment=edgeweight(edge_id),
                            )

            times.append(t)
            S.append(S[-1] - 1)
            I.append(I[-1] + 1)
            R.append(R[-1])

        total_rates[0] = gamma * infecteds.total_weight()  # I_weight_sum
        for size in unique_edge_sizes:
            total_rates[size] = (
                tau[size] * IS_links[size].total_weight()
            )  # IS_weight_sum

        total_rate = sum(total_rates.values())
        if total_rate > 0:
            delay = random.expovariate(total_rate)
        else:
            delay = float("Inf")
        t += delay

    if return_event_data:
        return events
    else:
        return np.array(times), np.array(S), np.array(I), np.array(R)


def Gillespie_SIS(
    H,
    tau,
    gamma,
    transmission_function=threshold,
    initial_infecteds=None,
    rho=None,
    tmin=0,
    tmax=100,
    recovery_weight=None,
    transmission_weight=None,
    return_event_data=False,
    seed=None,
    **args
):
    """Simulates the SIS model for hypergraphs with the Gillespie algorithm.

    Parameters
    ----------
    H : xgi.Hypergraph
        The hypergraph on which to simulate the SIR contagion process
    tau : dict
        Keys are edge sizes and values are transmission rates
    gamma : float
        Healing rate
    transmission_function : lambda function, default: threshold
        The contagion function that determines whether transmission is possible.
    initial_infecteds : iterable, default: None
        Initially infected node IDs.
    initial_recovereds : iterable, default: None
        Initially recovered node IDs.
    recovery_weight : hashable, default: None
        Hypergraph node attribute that weights the healing rate.
    transmission_weight : hashable, default: None
        Hypergraph edge attribute that weights the transmission rate.
    rho : float, default: None
        Fraction initially infected. Cannot be specified if
        `initial_infecteds` is defined.
    tmin : float, default: 0
        Time at which the simulation starts.
    tmax : float, default: float("Inf")
        Time at which the simulation terminates if there are still
        infected nodes.
    return_event_data : bool, default: False
        Whether to track each individual transition event that occurs.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.

    Returns
    -------
    tuple of np.arrays
        t, S, I

    Raises
    ------
    HyperContagionError
        If the user specifies both rho and initial_infecteds.
    """
    if seed is not None:
        random.seed(seed)

    members = H.edges.members(dtype=dict)
    memberships = H.nodes.memberships()

    if rho is not None and initial_infecteds is not None:
        raise HyperContagionError("cannot define both initial_infecteds and rho")

    if return_event_data:
        events = list()

    if transmission_weight is not None:

        def edgeweight(item):
            return item[transmission_weight]

    else:

        def edgeweight(item):
            return None

    if recovery_weight is not None:

        def nodeweight(u):
            return H.nodes[u][recovery_weight]

    else:

        def nodeweight(u):
            return None

    if initial_infecteds is None:
        if rho is None:
            initial_number = 1
        else:
            initial_number = int(round(H.num_nodes * rho))
        initial_infecteds = random.sample(list(H.nodes), initial_number)

    I = [len(initial_infecteds)]
    S = [H.num_nodes - I[0]]
    times = [tmin]

    t = tmin

    status = defaultdict(lambda: "S")
    for node in initial_infecteds:
        status[node] = "I"

        if return_event_data:
            events.append(
                {
                    "time": tmin,
                    "source": None,
                    "target": node,
                    "old_state": "S",
                    "new_state": "I",
                }
            )

    if return_event_data:
        for node in set(H.nodes).difference(initial_infecteds):
            events.append(
                {
                    "time": tmin,
                    "source": None,
                    "target": node,
                    "old_state": "I",
                    "new_state": "S",
                }
            )

    if recovery_weight is None:
        infecteds = SamplingDict()
    else:
        infecteds = SamplingDict(weighted=True)

    unique_edge_sizes = xgi.unique_edge_sizes(H)

    IS_links = dict()
    for size in unique_edge_sizes:
        if transmission_weight is None:
            IS_links[size] = SamplingDict()
        else:
            IS_links[size] = SamplingDict(weighted=True)

    for node in initial_infecteds:
        infecteds.update(node, weight_increment=nodeweight(node))
        for edge_id in memberships[
            node
        ]:  # must have this in a separate loop after assigning status of node
            # handle weighted vs. unweighted?
            edge = members[edge_id]
            for nbr in edge:  # there may be self-loops so account for this later
                if status[nbr] == "S":
                    contagion = transmission_function(nbr, status, edge, **args)
                    if contagion != 0:
                        IS_links[len(edge)].update(
                            (edge_id, nbr),
                            weight_increment=edgeweight(edge_id),
                        )  # need to be able to multiply by the contagion?

    total_rates = dict()
    total_rates[0] = gamma * infecteds.total_weight()  # I_weight_sum
    for size in unique_edge_sizes:
        total_rates[size] = tau[size] * IS_links[size].total_weight()  # IS_weight_sum

    total_rate = sum(total_rates.values())
    if total_rate > 0:
        delay = random.expovariate(total_rate)
    else:
        print("Total rate is zero and no events will happen!")
        delay = float("Inf")

    t += delay

    while infecteds and t < tmax:
        # rejection sampling
        while True:
            choice = random.choice(list(total_rates.keys()))
            if random.random() < total_rates[choice] / total_rate:
                break

        if choice == 0:  # recover
            recovering_node = (
                infecteds.random_removal()
            )  # chooses a node at random and removes it
            status[recovering_node] = "S"

            if return_event_data:
                events.append(
                    {
                        "time": t,
                        "source": None,
                        "target": recovering_node,
                        "old_state": "I",
                        "new_state": "S",
                    }
                )

            # Find the SI links for the recovered node to get reinfected
            for edge_id in memberships[recovering_node]:
                edge = members[edge_id]
                contagion = transmission_function(recovering_node, status, edge, **args)
                if contagion != 0:
                    IS_links[len(edge)].update(
                        (edge_id, recovering_node),
                        weight_increment=edgeweight(edge_id),
                    )

            # reduce the number of infected links because of the healing
            for edge_id in memberships[recovering_node]:
                edge = members[edge_id]
                for nbr in edge:
                    # if the key doesn't exist, don't attempt to remove it
                    if status[nbr] == "S" and (edge_id, nbr) in IS_links[len(edge)]:
                        contagion = transmission_function(nbr, status, edge, **args)
                        if contagion == 0:
                            try:
                                IS_links[len(edge)].remove((edge_id, nbr))
                            except:
                                pass

            times.append(t)
            S.append(S[-1] + 1)
            I.append(I[-1] - 1)
        else:
            source, recipient = IS_links[choice].choose_random()
            status[recipient] = "I"

            infecteds.update(recipient, weight_increment=nodeweight(recipient))

            if return_event_data:
                events.append(
                    {
                        "time": t,
                        "source": source,
                        "target": recipient,
                        "old_state": "S",
                        "new_state": "I",
                    }
                )

            for edge_id in memberships[recipient]:
                try:
                    IS_links[len(members[edge_id])].remove((edge_id, recipient))
                except:
                    pass

            for edge_id in memberships[recipient]:
                edge = members[edge_id]
                for nbr in edge:
                    if status[nbr] == "S":
                        contagion = transmission_function(nbr, status, edge, **args)
                        if contagion != 0:
                            IS_links[len(edge)].update(
                                (edge_id, nbr),
                                weight_increment=edgeweight(edge_id),
                            )
            times.append(t)
            S.append(S[-1] - 1)
            I.append(I[-1] + 1)

        total_rates[0] = gamma * infecteds.total_weight()
        for size in unique_edge_sizes:
            total_rates[size] = tau[size] * IS_links[size].total_weight()
        total_rate = sum(total_rates.values())
        if total_rate > 0:
            delay = random.expovariate(total_rate)
        else:
            delay = float("Inf")
        t += delay

    if return_event_data:
        return events
    else:
        return np.array(times), np.array(S), np.array(I)


def event_driven_SIR(
    H,
    tau,
    gamma,
    transmission_function=majority_vote,
    initial_infecteds=None,
    initial_recovereds=None,
    rho=None,
    tmin=0,
    tmax=float("Inf"),
    return_event_data=False,
    seed=None,
    **args
):
    """Simulates the SIR model for hypergraphs with the event-driven algorithm.

    Parameters
    ----------
    H : xgi.Hypergraph
        The hypergraph on which to simulate the SIR contagion process
    tau : dict
        Keys are edge sizes and values are transmission rates
    gamma : float
        Healing rate
    transmission_function : lambda function, default: threshold
        The contagion function that determines whether transmission is possible.
    initial_infecteds : iterable, default: None
        Initially infected node IDs.
    initial_recovereds : iterable, default: None
        Initially recovered node IDs.
    recovery_weight : hashable, default: None
        Hypergraph node attribute that weights the healing rate.
    transmission_weight : hashable, default: None
        Hypergraph edge attribute that weights the transmission rate.
    rho : float, default: None
        Fraction initially infected. Cannot be specified if
        `initial_infecteds` is defined.
    tmin : float, default: 0
        Time at which the simulation starts.
    tmax : float, default: float("Inf")
        Time at which the simulation terminates if there are still
        infected nodes.
    return_event_data : bool, default: False
        Whether to track each individual transition event that occurs.

    Returns
    -------
    tuple of np.arrays
        t, S, I, R

    Raises
    ------
    HyperContagionError
        If the user specifies both rho and initial_infecteds.
    """
    if seed is not None:
        random.seed(seed)

    if rho is not None and initial_infecteds is not None:
        raise HyperContagionError("cannot define both initial_infecteds and rho")

    events = list()

    # now we define the initial setup.
    status = defaultdict(lambda: "S")  # node status defaults to 'S'
    rec_time = defaultdict(lambda: tmin - 1)  # node recovery time defaults to -1
    if initial_recovereds is not None:
        for node in initial_recovereds:
            status[node] = "R"
            rec_time[node] = (
                tmin - 1
            )  # default value for these.  Ensures that the recovered nodes appear with a time
            events.append((tmin, None, node, "I", "R"))
    pred_inf_time = defaultdict(lambda: float("Inf"))
    # infection time defaults to \infty  --- this could be set to tmax,
    # probably with a slight improvement to performance.

    Q = EventQueue(tmax)

    if initial_infecteds is None:
        if rho is None:
            initial_number = 1
        else:
            initial_number = int(round(H.num_nodes * rho))
        initial_infecteds = random.sample(list(H.nodes), initial_number)

    if initial_recovereds is None:
        initial_recovereds = []

    I = [0]
    R = [0]
    S = [H.num_nodes]
    times = [tmin]

    for u in initial_infecteds:
        pred_inf_time[u] = tmin
        Q.add(
            tmin,
            _process_trans_SIR_,
            args=(
                times,
                S,
                I,
                R,
                Q,
                H,
                status,
                transmission_function,
                gamma,
                tau,
                None,
                u,
                rec_time,
                pred_inf_time,
                events,
            ),
        )

    while Q:  # all the work is done in this while loop.
        Q.pop_and_run()

    if return_event_data:
        return events
    else:
        times = times[len(initial_infecteds) :]
        S = S[len(initial_infecteds) :]
        I = I[len(initial_infecteds) :]
        R = R[len(initial_infecteds) :]
        return np.array(times), np.array(S), np.array(I), np.array(R)


def event_driven_SIS(
    H,
    tau,
    gamma,
    transmission_function=majority_vote,
    initial_infecteds=None,
    rho=None,
    tmin=0,
    tmax=float("Inf"),
    return_event_data=False,
    seed=None,
    **args
):
    """Simulates the SIS model for hypergraphs with the event-driven algorithm.

    Parameters
    ----------
    H : xgi.Hypergraph
        The hypergraph on which to simulate the SIR contagion process
    tau : dict
        Keys are edge sizes and values are transmission rates
    gamma : float
        Healing rate
    transmission_function : lambda function, default: threshold
        The contagion function that determines whether transmission is possible.
    initial_infecteds : iterable, default: None
        Initially infected node IDs.
    initial_recovereds : iterable, default: None
        Initially recovered node IDs.
    recovery_weight : hashable, default: None
        Hypergraph node attribute that weights the healing rate.
    transmission_weight : hashable, default: None
        Hypergraph edge attribute that weights the transmission rate.
    rho : float, default: None
        Fraction initially infected. Cannot be specified if
        `initial_infecteds` is defined.
    tmin : float, default: 0
        Time at which the simulation starts.
    tmax : float, default: float("Inf")
        Time at which the simulation terminates if there are still
        infected nodes.
    return_event_data : bool, default: False
        Whether to track each individual transition event that occurs.

    Returns
    -------
    tuple of np.arrays
        t, S, I

    Raises
    ------
    HyperContagionError
        If the user specifies both rho and initial_infecteds.
    """
    if seed is not None:
        random.seed(seed)

    if rho is not None and initial_infecteds is not None:
        raise HyperContagionError("cannot define both initial_infecteds and rho")

    events = list()

    # now we define the initial setup.
    status = defaultdict(lambda: "S")  # node status defaults to 'S'
    rec_time = defaultdict(lambda: tmin - 1)  # node recovery time defaults to -1

    pred_inf_time = defaultdict(lambda: float("Inf"))
    # infection time defaults to \infty  --- this could be set to tmax,
    # probably with a slight improvement to performance.

    Q = EventQueue(tmax)

    if initial_infecteds is None:
        if rho is None:
            initial_number = 1
        else:
            initial_number = int(round(H.num_nodes * rho))
        initial_infecteds = random.sample(list(H.nodes), initial_number)

    I = [0]
    S = [H.num_nodes]
    times = [tmin]

    for u in initial_infecteds:
        pred_inf_time[u] = tmin
        Q.add(
            tmin,
            _process_trans_SIS_,
            args=(
                times,
                S,
                I,
                Q,
                H,
                status,
                transmission_function,
                gamma,
                tau,
                None,
                u,
                rec_time,
                pred_inf_time,
                events,
            ),
        )

    while Q:  # all the work is done in this while loop.
        Q.pop_and_run()

    if return_event_data:
        return events
    else:
        times = times[len(initial_infecteds) :]
        S = S[len(initial_infecteds) :]
        I = I[len(initial_infecteds) :]
        return np.array(times), np.array(S), np.array(I)

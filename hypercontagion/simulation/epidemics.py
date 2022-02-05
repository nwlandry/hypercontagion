# import networkx as nx
import random
import numpy as np
from collections import defaultdict
from hypercontagion.exception import HyperContagionError
from hypercontagion.simulation.functions import threshold
from hypercontagion.utilities import _ListDict_
import xgi


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
    **args
):

    if rho is not None and initial_infecteds is not None:
        raise HyperContagionError("cannot define both initial_infecteds and rho")

    gamma = float(gamma)

    if initial_infecteds is None:
        if rho is None:
            initial_number = 1
        else:
            initial_number = int(round(H.number_of_nodes() * rho))
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

    I = [len(initial_infecteds)]
    S = [H.number_of_nodes() - I[0]]
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
                else:
                    new_status[node] = "I"
            else:
                # infect by neighbors of all sizes
                for edge_id in H.nodes.membership(node):
                    edge = H.edges.members(edge_id)
                    if tau[len(edge)] > 0:
                        if random.random() <= tau[len(edge)] \
                        * transmission_function(node, status, edge, **args) \
                        * dt * edgeweight(edge_id):
                            new_status[node] = "I"
                            S[-1] += -1
                            I[-1] += 1
                            break
                else:
                    new_status[node] == "S"
        status = new_status.copy()
        t += dt
        times.append(t)

    return np.array(times), np.array(S), np.array(I)


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
    **args
):

    if rho is not None and initial_infecteds is not None:
        raise HyperContagionError("cannot define both initial_infecteds and rho")

    gamma = float(gamma)

    if initial_infecteds is None:
        if rho is None:
            initial_number = 1
        else:
            initial_number = int(round(H.number_of_nodes() * rho))
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
    for node in initial_recovereds:
        status[node] = "R"

    I = [len(initial_infecteds)]
    R = [len(initial_recovereds)]
    S = [H.number_of_nodes() - I[0] - R[0]]
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
                else:
                    new_status[node] = "I"
            elif status[node] == "S":
                # infect by neighbors of all sizes
                for edge_id in H.nodes.membership(node):
                    edge = H.edges.members(edge_id)
                    if tau[len(edge)] > 0:
                        if random.random() <= tau[len(edge)] \
                            * transmission_function(node, status, edge, **args) \
                            * dt * edgeweight(edge_id):
                            new_status[node] = "I"
                            S[-1] += -1
                            I[-1] += 1
                            break
                else:
                    new_status[node] == "S"
        status = new_status.copy()
        t += dt
        times.append(t)

    return np.array(times), np.array(S), np.array(I), np.array(R)


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
    **args
):
    if rho is not None and initial_infecteds is not None:
        raise HyperContagionError("cannot define both initial_infecteds and rho")

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
            initial_number = int(round(H.number_of_nodes() * rho))
        initial_infecteds = random.sample(list(H.nodes), initial_number)

    if initial_recovereds is None:
        initial_recovereds = []

    I = [len(initial_infecteds)]
    R = [len(initial_recovereds)]
    S = [H.number_of_nodes() - I[0] - R[0]]
    times = [tmin]

    t = tmin

    status = defaultdict(lambda: "S")
    for node in initial_infecteds:
        status[node] = "I"
    for node in initial_recovereds:
        status[node] = "R"
    if recovery_weight is None:
        infecteds = _ListDict_()
    else:
        infecteds = _ListDict_(weighted=True)

    unique_edge_sizes = xgi.unique_edge_sizes(H)
    IS_links = dict()
    for size in unique_edge_sizes:
        if transmission_weight is None:
            IS_links[size] = _ListDict_()
        else:
            IS_links[size] = _ListDict_(weighted=True)

    for node in initial_infecteds:
        infecteds.update(node, weight_increment=nodeweight(node))
        for edge_id in H.nodes.membership(node):
            edge = H.edges.members(edge_id)
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
            
            for edge_id in H.nodes.membership(recovering_node):
                edge = H.edges.members(edge_id)
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
            _, recipient = IS_links[choice].choose_random()  # we don't use remove since that complicates the later removal of edges.
            status[recipient] = "I"

            infecteds.update(recipient, weight_increment=nodeweight(recipient))

            for edge_id in H.nodes.membership(recipient):
                try:
                    IS_links[len(H.edges.members(edge_id))].remove((edge_id, recipient))
                except:
                    pass

            for edge_id in H.nodes.membership(recipient):
                edge = H.edges.members(edge_id)
                for nbr in edge:
                    if status[nbr] == "S":
                        contagion = transmission_function(nbr, status, edge, **args)
                        if contagion != 0:
                            IS_links[len(edge)].update((edge_id, nbr),
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
    **args
):
    if rho is not None and initial_infecteds is not None:
        raise HyperContagionError("cannot define both initial_infecteds and rho")

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
            initial_number = int(round(H.number_of_nodes() * rho))
        initial_infecteds = random.sample(list(H.nodes), initial_number)

    I = [len(initial_infecteds)]
    S = [H.number_of_nodes() - I[0]]
    times = [tmin]

    t = tmin

    status = defaultdict(lambda: "S")
    for node in initial_infecteds:
        status[node] = "I"

    if recovery_weight is None:
        infecteds = _ListDict_()
    else:
        infecteds = _ListDict_(weighted=True)

    unique_edge_sizes = xgi.unique_edge_sizes(H)

    IS_links = dict()
    for size in unique_edge_sizes:
        if transmission_weight is None:
            IS_links[size] = _ListDict_()
        else:
            IS_links[size] = _ListDict_(weighted=True)

    for node in initial_infecteds:
        infecteds.update(node, weight_increment=nodeweight(node))
        for edge_id in H.nodes.membership(node):  # must have this in a separate loop after assigning status of node
            # handle weighted vs. unweighted?
            edge = H.edges.members(edge_id)
            for nbr in edge:  # there may be self-loops so account for this later
                if status[nbr] == "S":
                    contagion = transmission_function(node, status, edge, **args)
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

            # Find the SI links for the recovered node to get reinfected
            for edge_id in H.nodes.membership(recovering_node):
                edge = H.edges.members(edge_id)
                contagion = transmission_function(recovering_node, status, edge, **args)
                if contagion != 0:
                    IS_links[len(edge)].update(
                    (edge_id, recovering_node),
                    weight_increment=edgeweight(edge_id),
                )

            # reduce the number of infected links because of the healing
            for edge_id in H.nodes.membership(recovering_node):
                edge = H.edges.members(edge_id)
                for nbr in edge:
                    # if the key doesn't exist, don't attempt to remove it
                    if status[nbr] == "S" and (edge_id, nbr) in IS_links[len(edge)]:
                        contagion = transmission_function(nbr, status, edge, **args)
                        if contagion == 0:
                            try:
                                IS_links[len(edge)].remove(
                                    (edge_id, nbr)
                                )
                            except:
                                pass

            times.append(t)
            S.append(S[-1] + 1)
            I.append(I[-1] - 1)
        else:
            transmitter, recipient = IS_links[choice].choose_random()
            status[recipient] = "I"

            infecteds.update(recipient, weight_increment=nodeweight(recipient))

            for edge_id in H.nodes.membership(recipient):
                try:
                    IS_links[len(H.edges.members(edge_id))].remove((edge_id, recipient))
                except:
                    pass

            for edge_id in H.nodes.membership(recipient):
                edge = H.edges.members(edge_id)
                for nbr in edge:
                    if status[nbr] == "S":
                        contagion = transmission_function(node, status, edge, **args)
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
    return np.array(times), np.array(S), np.array(I)

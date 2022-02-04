# import networkx as nx
import random
import heapq
import numpy as np
from collections import defaultdict
from collections import Counter
from hypercontagion.exception import HyperContagionError, HyperContagionException
from hypercontagion.simulation.functions import threshold

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


# def Gillespie_SIR(
#     H,
#     tau,
#     gamma,
#     transmission_function=threshold,
#     initial_infecteds=None,
#     initial_recovereds=None,
#     rho=None,
#     tmin=0,
#     tmax=float("Inf"),
#     recovery_weight=None,
#     transmission_weight=None,
#     **args
# ):
#     if rho is not None and initial_infecteds is not None:
#         raise HyperContagionError("cannot define both initial_infecteds and rho")

#     if transmission_weight is not None:

#         def edgeweight(item):
#             return item[transmission_weight]

#     else:

#         def edgeweight(item):
#             return None

#     if recovery_weight is not None:

#         def nodeweight(u):
#             return H.nodes[u][recovery_weight]

#     else:

#         def nodeweight(u):
#             return None

#     if initial_infecteds is None:
#         if rho is None:
#             initial_number = 1
#         else:
#             initial_number = int(round(H.number_of_nodes() * rho))
#         initial_infecteds = random.sample(list(H.nodes), initial_number)

#     if initial_recovereds is None:
#         initial_recovereds = []

#     I = [len(initial_infecteds)]
#     R = [len(initial_recovereds)]
#     S = [H.number_of_nodes() - I[0] - R[0]]
#     times = [tmin]

#     transmissions = []
#     t = tmin

#     status = defaultdict(lambda: "S")
#     for node in initial_infecteds:
#         status[node] = "I"
#     for node in initial_recovereds:
#         status[node] = "R"
#     if recovery_weight is None:
#         infecteds = _ListDict_()
#     else:
#         infecteds = _ListDict_(weighted=True)

#     IS_links = dict()
#     for size in H.getHyperedgeSizes():
#         if transmission_weight is None:
#             IS_links[size] = _ListDict_()
#         else:
#             IS_links[size] = _ListDict_(weighted=True)

#     for node in initial_infecteds:
#         infecteds.update(node, weight_increment=nodeweight(node))
#         for uid, nbrData in H.neighbors[
#             node
#         ].items():  # must have this in a separate loop after assigning status of node
#             # handle weighted vs. unweighted?
#             for nbr in nbrData[
#                 "neighbors"
#             ]:  # there may be self-loops so account for this later
#                 if status[nbr] == "S":
#                     contagion = transmission_function(
#                         status, H.neighbors[nbr][uid]["neighbors"], **args
#                     )
#                     if contagion != 0:
#                         IS_links[len(nbrData["neighbors"]) + 1].update(
#                             (H.neighbors[nbr][uid]["neighbors"], nbr),
#                             weight_increment=edgeweight(nbrData),
#                         )  # need to be able to multiply by the contagion?

#     total_rates = dict()
#     total_rates[1] = gamma * infecteds.total_weight()  # I_weight_sum
#     for size in H.getHyperedgeSizes():
#         total_rates[size] = tau[size] * IS_links[size].total_weight()  # IS_weight_sum

#     total_rate = sum(total_rates.values())

#     delay = random.expovariate(total_rate)
#     t += delay

#     while infecteds and t < tmax:
#         while True:
#             choice = random.choice(
#                 list(total_rates.keys())
#             )  # Is there a faster way to do this?
#             if random.random() < total_rates[choice] / total_rate:
#                 break
#         if choice == 1:  # recover
#             recovering_node = (
#                 infecteds.random_removal()
#             )  # does weighted choice and removes it
#             status[recovering_node] = "R"

#             for uid, nbrData in H.neighbors[recovering_node].items():
#                 for nbr in nbrData["neighbors"]:
#                     if (
#                         status[nbr] == "S"
#                         and (H.neighbors[nbr][uid]["neighbors"], nbr)
#                         in IS_links[len(nbrData["neighbors"]) + 1]
#                     ):
#                         contagion = transmission_function(
#                             status, H.neighbors[nbr][uid]["neighbors"], **args
#                         )
#                         if contagion == 0:
#                             try:
#                                 IS_links[len(nbrData["neighbors"]) + 1].remove(
#                                     (H.neighbors[nbr][uid]["neighbors"], nbr)
#                                 )
#                             except:
#                                 pass

#             times.append(t)
#             S.append(S[-1])
#             I.append(I[-1] - 1)
#             R.append(R[-1] + 1)
#         else:  # transmit
#             transmitter, recipient = IS_links[
#                 choice
#             ].choose_random()  # we don't use remove since that complicates the later removal of edges.
#             status[recipient] = "I"

#             infecteds.update(recipient, weight_increment=nodeweight(recipient))

#             for uid, nbrData in H.neighbors[recipient].items():
#                 try:
#                     IS_links[len(nbrData["neighbors"]) + 1].remove(
#                         (nbrData["neighbors"], recipient)
#                     )  # multiply by contagion?
#                 except:
#                     pass

#             for uid, nbrData in H.neighbors[recipient].items():
#                 for nbr in nbrData["neighbors"]:
#                     if status[nbr] == "S":
#                         contagion = transmission_function(
#                             status, H.neighbors[nbr][uid]["neighbors"], **args
#                         )
#                         if contagion != 0:
#                             IS_links[len(nbrData["neighbors"]) + 1].update(
#                                 (H.neighbors[nbr][uid]["neighbors"], nbr),
#                                 weight_increment=edgeweight(nbrData),
#                             )

#             times.append(t)
#             S.append(S[-1] - 1)
#             I.append(I[-1] + 1)
#             R.append(R[-1])

#         total_rates[1] = gamma * infecteds.total_weight()  # I_weight_sum
#         for size in H.getHyperedgeSizes():
#             total_rates[size] = (
#                 tau[size] * IS_links[size].total_weight()
#             )  # IS_weight_sum

#         total_rate = sum(total_rates.values())
#         if total_rate > 0:
#             delay = random.expovariate(total_rate)
#         else:
#             delay = float("Inf")
#         t += delay

#     return np.array(times), np.array(S), np.array(I), np.array(R)


# def Gillespie_SIS(
#     H,
#     tau,
#     gamma,
#     transmission_function=threshold,
#     initial_infecteds=None,
#     rho=None,
#     tmin=0,
#     tmax=100,
#     recovery_weight=None,
#     transmission_weight=None,
#     **args
# ):
#     if rho is not None and initial_infecteds is not None:
#         raise HyperContagionError("cannot define both initial_infecteds and rho")

#     if transmission_weight is not None:

#         def edgeweight(item):
#             return item[transmission_weight]

#     else:

#         def edgeweight(item):
#             return None

#     if recovery_weight is not None:

#         def nodeweight(u):
#             return H.nodes[u][recovery_weight]

#     else:

#         def nodeweight(u):
#             return None

#     if initial_infecteds is None:
#         if rho is None:
#             initial_number = 1
#         else:
#             initial_number = int(round(H.number_of_nodes() * rho))
#         initial_infecteds = random.sample(H.nodeLabels, initial_number)

#     I = [len(initial_infecteds)]
#     S = [H.number_of_nodes() - I[0]]
#     times = [tmin]

#     t = tmin
#     transmissions = []

#     status = defaultdict(lambda: "S")
#     for node in initial_infecteds:
#         status[node] = "I"

#     if recovery_weight is None:
#         infecteds = _ListDict_()
#     else:
#         infecteds = _ListDict_(weighted=True)

#     IS_links = dict()
#     for size in np.unique(list(H.edge_sizes)):
#         if transmission_weight is None:
#             IS_links[size] = _ListDict_()
#         else:
#             IS_links[size] = _ListDict_(weighted=True)

#     for node in initial_infecteds:
#         infecteds.update(node, weight_increment=nodeweight(node))
#         for edges in H.nodes[node]:  # must have this in a separate loop after assigning status of node
#             # handle weighted vs. unweighted?
#             for e in edges:  # there may be self-loops so account for this later
#                 edge = H.edges[e]
#                 for nbr in set(edge).difference({node}):
#                     if status[nbr] == "S":
#                         contagion = transmission_function(node,
#                         status, edge, **args
#                     )
#                     if contagion != 0:
#                         IS_links[len(edge)].update(
#                             (H.e, nbr),
#                             weight_increment=edgeweight(e),
#                         )  # need to be able to multiply by the contagion?

#     total_rates = dict()
#     total_rates[1] = gamma * infecteds.total_weight()  # I_weight_sum
#     for size in H.getHyperedgeSizes():
#         total_rates[size] = tau[size] * IS_links[size].total_weight()  # IS_weight_sum

#     total_rate = sum(total_rates.values())

#     delay = random.expovariate(total_rate)
#     t += delay

#     while infecteds and t < tmax:
#         # rejection sampling
#         while True:
#             choice = random.choice(list(total_rates.keys()))
#             if random.random() < total_rates[choice] / total_rate:
#                 break

#         if choice == 1:  # recover
#             recovering_node = (
#                 infecteds.random_removal()
#             )  # chooses a node at random and removes it
#             status[recovering_node] = "S"

#             # Find the SI links for the recovered node to get reinfected
#             for edges in H.nodes[recovering_node]:
#                 # if recipient in set(nbrData["neighbors"]):  #move past self edges
#                 #     continue
#                 # Not sure about this...
#                 for e in edges:
#                     edge = H.edges[e]
#                     contagion = transmission_function(recovering_node, status, edge, **args)
#                     if contagion != 0:
#                         IS_links[len(edge)].update(
#                         (e, recovering_node),
#                         weight_increment=edgeweight(e),
#                     )

#             # reduce the number of infected links because of the healing
#             for edges in H.nodes[recovering_node]:
#                 for edge in edges:
#                 for nbr in nbrData["neighbors"]:
#                     if (
#                         status[nbr] == "S"
#                         and (e, nbr)
#                         in IS_links[len(nbrData["neighbors"]) + 1]
#                     ):  # if the key doesn't exist, don't attempt to remove it
#                         contagion = transmission_function(
#                             status, H.neighbors[nbr][uid]["neighbors"], **args
#                         )
#                         if contagion == 0:
#                             try:
#                                 IS_links[len(nbrData["neighbors"]) + 1].remove(
#                                     (H.neighbors[nbr][uid]["neighbors"], nbr)
#                                 )  # should this be "update" instead of "remove"?
#                             except:
#                                 pass

#             times.append(t)
#             S.append(S[-1] + 1)
#             I.append(I[-1] - 1)
#         else:
#             transmitter, recipient = IS_links[choice].choose_random()
#             status[recipient] = "I"

#             infecteds.update(recipient, weight_increment=nodeweight(recipient))

#             for uid, nbrData in H.neighbors[recipient].items():
#                 # if recipient in set(nbrData["neighbors"]):  #move past self edges
#                 #     continue
#                 # the above line messed up the simulation
#                 try:
#                     IS_links[len(nbrData["neighbors"]) + 1].remove(
#                         (nbrData["neighbors"], recipient)
#                     )  # multiply by contagion?
#                 except:
#                     pass

#             for uid, nbrData in H.neighbors[recipient].items():
#                 for nbr in nbrData["neighbors"]:
#                     if status[nbr] == "S":
#                         contagion = transmission_function(
#                             status, H.neighbors[nbr][uid]["neighbors"], **args
#                         )
#                         if contagion != 0:
#                             IS_links[len(nbrData["neighbors"]) + 1].update(
#                                 (H.neighbors[nbr][uid]["neighbors"], nbr),
#                                 weight_increment=edgeweight(nbrData),
#                             )
#             times.append(t)
#             S.append(S[-1] - 1)
#             I.append(I[-1] + 1)

#         total_rates[1] = gamma * infecteds.total_weight()
#         for size in H.getHyperedgeSizes():
#             total_rates[size] = tau[size] * IS_links[size].total_weight()
#         total_rate = sum(total_rates.values())
#         if total_rate > 0:
#             delay = random.expovariate(total_rate)
#         else:
#             delay = float("Inf")
#         t += delay
#     return np.array(times), np.array(S), np.array(I)

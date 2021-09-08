#import networkx as nx
import random
import heapq
import numpy as np
from collections import defaultdict
from collections import Counter
from exception import HyperContagionError, HyperContagionException

#######################
#                     #
#   Auxiliary stuff   #
#                     #
#######################

# built-in functions
def collective_contagion(status, neighbors):
    for i in neighbors:
        if status[i] != 'I':
            return 0
    return 1

def individual_contagion(status, neighbors):
    for i in neighbors:
        if status[i] == 'I':
            return 1
    return 0

def threshold(status, neighbors, threshold=0.5):
    meanContagion = sum([status[i] == 'I' for i in neighbors])/len(neighbors)
    if meanContagion < threshold:
        return 0
    elif meanContagion >= threshold:
        return 1

def majority_vote(status, neighbors):
    meanContagion = sum([status[i] == 'I' for i in neighbors])/len(neighbors)
    if meanContagion < 0.5:
        return 0
    elif meanContagion > 0.5:
        return 1
    else:
        return random.choice([0, 1])

def size_dependent(status, neighbors):
    return sum([status[i] == 'I' for i in neighbors])

class _ListDict_(object):
    r'''
    The Gillespie algorithm will involve a step that samples a random element
    from a set based on its weight.  This is awkward in Python.

    So I'm introducing a new class based on a stack overflow answer by
    Amber (http://stackoverflow.com/users/148870/amber)
    for a question by
    tba (http://stackoverflow.com/users/46521/tba)
    found at
    http://stackoverflow.com/a/15993515/2966723

    This will allow me to select a random element uniformly, and then use
    rejection sampling to make sure it's been selected with the appropriate
    weight.
    '''
    def __init__(self, weighted = False):
        self.item_to_position = {}
        self.items = []

        self.weighted = weighted
        if self.weighted:
            self.weight = defaultdict(int) #presume all weights positive
            self.max_weight = 0
            self._total_weight = 0
            self.max_weight_count = 0


    def __len__(self):
        return len(self.items)

    def __contains__(self, item):
        return item in self.item_to_position

    def _update_max_weight(self):
        C = Counter(self.weight.values())  #may be a faster way to do this, we only need to count the max.
        self.max_weight = max(C.keys())
        self.max_weight_count = C[self.max_weight]


    def insert(self, item, weight = None):
        r'''
        If not present, then inserts the thing (with weight if appropriate)
        if already there, replaces the weight unless weight is 0

        If weight is 0, then it removes the item and doesn't replace.

        WARNING:
            replaces weight if already present, does not increment weight.


        '''
        if self.__contains__(item):
            self.remove(item)
        if weight != 0:
            self.update(item, weight_increment=weight)


    def update(self, item, weight_increment = None):
        r'''
        If not present, then inserts the thing (with weight if appropriate)
        if already there, increments weight

        WARNING:
            increments weight if already present, cannot overwrite weight.
        '''
        if weight_increment is not None: #will break if passing a weight to unweighted case
            if weight_increment > 0 or self.weight[item] != self.max_weight:
                self.weight[item] = self.weight[item] + weight_increment
                self._total_weight += weight_increment
                if self.weight[item] > self.max_weight:
                    self.max_weight_count = 1
                    self.max_weight = self.weight[item]
                elif self.weight[item] == self.max_weight:
                    self.max_weight_count += 1
            else: #it's a negative increment and was at max
                self.max_weight_count -= 1
                self.weight[item] = self.weight[item] + weight_increment
                self._total_weight += weight_increment
                self.max_weight_count -= 1
                if self.max_weight_count == 0:
                    self._update_max_weight
        elif self.weighted:
            raise Exception('if weighted, must assign weight_increment')

        if item in self: #we've already got it, do nothing else
            return
        self.items.append(item)
        self.item_to_position[item] = len(self.items)-1

    def remove(self, choice):
        position = self.item_to_position.pop(choice) # why don't we pop off the last item and put it in the choice index?
        last_item = self.items.pop()
        if position != len(self.items):
            self.items[position] = last_item
            self.item_to_position[last_item] = position

        if self.weighted:
            weight = self.weight.pop(choice)
            self._total_weight -= weight
            if weight == self.max_weight:
                #if we find ourselves in this case often
                #it may be better just to let max_weight be the
                #largest weight *ever* encountered, even if all remaining weights are less
                #
                self.max_weight_count -= 1
                if self.max_weight_count == 0 and len(self)>0:
                    self._update_max_weight()

    def choose_random(self):
        # r'''chooses a random node.  If there is a weight, it will use rejection
        # sampling to choose a random node until it succeeds'''
        if self.weighted:
            while True:
                choice = random.choice(self.items)
                if random.random() < self.weight[choice]/self.max_weight:
                    break
            # r = random.random()*self.total_weight
            # for item in self.items:
            #     r-= self.weight[item]
            #     if r<0:
            #         break
            return choice

        else:
            return random.choice(self.items)


    def random_removal(self):
        r'''uses other class methods to choose and then remove a random node'''
        choice = self.choose_random()
        self.remove(choice)
        return choice

    def total_weight(self):
        if self.weighted:
            return self._total_weight
        else:
            return len(self)
    def update_total_weight(self):
        self._total_weight = sum(self.weight[item] for item in self.items)

##########################
#                        #
#    SIMULATION CODE     #
#                        #
##########################

'''
    The code in the region below is used for stochastic simulation of
    epidemics on networks
'''

def discrete_SIS1(H, tau, gamma, transmission_function=threshold, initial_infecteds=None, recovery_weight=None, transmission_weight = None, rho=None, tmin=0, tmax=float('Inf'), dt=1.0, **args):

    if rho is not None and initial_infecteds is not None:
        raise HyperContagionError("cannot define both initial_infecteds and rho")

    gamma = float(gamma)

    if initial_infecteds is None:
        if rho is None:
            initial_number = 1
        else:
            initial_number = int(round(H.number_of_nodes()*rho))
        initial_infecteds=random.sample(list(H.nodes), initial_number)        

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

    status = defaultdict(lambda : 'S')
    for node in initial_infecteds:
        status[node] = 'I'

    I = [len(initial_infecteds)]
    S = [H.number_of_nodes()-I[0]]
    times = [tmin]
    t = tmin
    newStatus = status

    while t <= tmax and I[-1] != 0:
        S.append(S[-1])
        I.append(I[-1])

        for node in H.nodes:
            if status[node] == "I":
                # heal
                if random.random() <= gamma*dt*nodeweight(node):
                    newStatus[node] = "S"
                    S[-1] += 1
                    I[-1] += -1
                else:
                    newStatus[node] = "I"
            else:
                # infect by neighbors of all sizes
                for edge in H.nodes[node]:
                    if tau[len(H.edges[edge])] > 0:
                        if random.random() <= tau[len(H.edges[edge])]*transmission_function(status, H.edges[edge].elements.difference({node}), **args)*dt*edgeweight(edge):
                            newStatus[node] = "I"
                            S[-1] += -1
                            I[-1] += 1
                            break
                else:
                    newStatus[node] == "S"
        status = newStatus.copy()
        t += dt
        times.append(t)

    return np.array(times), np.array(S), np.array(I)

def discrete_SIR(H, tau, gamma, transmission_function=collective_contagion, initial_infecteds=None, initial_recovereds=None, recovery_weight=None, transmission_weight = None, rho=None, tmin=0, tmax=float('Inf'), dt=1.0, **args):

    if rho is not None and initial_infecteds is not None:
        raise HyperContagionError("cannot define both initial_infecteds and rho")

    gamma = float(gamma)

    if initial_infecteds is None:
        if rho is None:
            initial_number = 1
        else:
            initial_number = int(round(H.number_of_nodes()*rho))
        initial_infecteds=random.sample(H.nodeLabels, initial_number)

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

    status = defaultdict(lambda : 'S')
    for node in initial_infecteds:
        status[node] = 'I'
    for node in initial_recovereds:
        status[node] = 'R'

    timesteps = int((tmax-tmin)/dt)

    I = [len(initial_infecteds)]
    R = [len(initial_recovereds)]
    S = [H.number_of_nodes()-I[0]-R[0]]
    times = [tmin]
    t = tmin
    newStatus = status

    while t <= tmax and I[-1] != 0:
        S.append(S[-1])
        I.append(I[-1])
        R.append(R[-1])

        for node in H.nodeLabels:
            if status[node] == "I":
                # heal
                if random.random() <= gamma*dt*nodeweight(node):
                    newStatus[node] = "R"
                    R[-1] += 1
                    I[-1] += -1
                else:
                    newStatus[node] = "I"
            elif status[node] == "S":
                # infect by neighbors of all sizes
                for uid, nbrs in H.neighbors[node].items():
                    if tau[len(nbrs["neighbors"])+1] != 0:
                        if random.random() <= tau[len(nbrs["neighbors"])+1]*transmission_function(status, nbrs["neighbors"], **args)*dt*edgeweight(nbrs):
                            newStatus[node] = "I"
                            S[-1] += -1
                            I[-1] += 1
                            break
                else:
                    newStatus[node] == "S"
        status = newStatus.copy()
        t += dt
        times.append(t)

    return np.array(times), np.array(S), np.array(I), np.array(R)


def Gillespie_SIR(H, tau, gamma, transmission_function=threshold, initial_infecteds=None, initial_recovereds = None, rho = None, tmin = 0, tmax=float('Inf'), recovery_weight = None, transmission_weight = None, **args):
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
            initial_number = int(round(H.number_of_nodes()*rho))
        initial_infecteds=random.sample(H.nodeLabels, initial_number)

    if initial_recovereds is None:
        initial_recovereds = []

    I = [len(initial_infecteds)]
    R = [len(initial_recovereds)]
    S = [H.number_of_nodes()-I[0]-R[0]]
    times = [tmin]

    transmissions = []
    t = tmin

    status = defaultdict(lambda : 'S')
    for node in initial_infecteds:
        status[node] = 'I'
    for node in initial_recovereds:
        status[node] = 'R'
    if recovery_weight is None:
        infecteds = _ListDict_()
    else:
        infecteds = _ListDict_(weighted=True)

    IS_links = dict()
    for size in H.getHyperedgeSizes():
        if transmission_weight is None:
            IS_links[size] = _ListDict_()
        else:
            IS_links[size] = _ListDict_(weighted=True)

    for node in initial_infecteds:
        infecteds.update(node, weight_increment = nodeweight(node))
        for uid, nbrData in H.neighbors[node].items():  #must have this in a separate loop after assigning status of node
        # handle weighted vs. unweighted?
            for nbr in nbrData["neighbors"]: # there may be self-loops so account for this later
                if status[nbr] == 'S':
                    contagion = transmission_function(status, H.neighbors[nbr][uid]["neighbors"], **args)
                    if contagion != 0:
                        IS_links[len(nbrData["neighbors"])+1].update((H.neighbors[nbr][uid]["neighbors"], nbr), weight_increment=edgeweight(nbrData)) # need to be able to multiply by the contagion?

    total_rates = dict()
    total_rates[1] = gamma*infecteds.total_weight()#I_weight_sum
    for size in H.getHyperedgeSizes():
        total_rates[size] = tau[size]*IS_links[size].total_weight() #IS_weight_sum

    total_rate = sum(total_rates.values())

    delay = random.expovariate(total_rate)
    t += delay

    while infecteds and t<tmax:
        while True:
            choice = random.choice(list(total_rates.keys())) # Is there a faster way to do this?
            if random.random() < total_rates[choice]/total_rate:
                break
        if choice == 1: #recover
            recovering_node = infecteds.random_removal() #does weighted choice and removes it
            status[recovering_node]='R'

            for uid, nbrData in H.neighbors[recovering_node].items():
                for nbr in nbrData["neighbors"]:
                    if status[nbr] == 'S' and (H.neighbors[nbr][uid]["neighbors"], nbr) in IS_links[len(nbrData["neighbors"])+1]:
                        contagion = transmission_function(status, H.neighbors[nbr][uid]["neighbors"], **args)
                        if contagion == 0:
                            try:
                                IS_links[len(nbrData["neighbors"])+1].remove((H.neighbors[nbr][uid]["neighbors"], nbr))
                            except:
                                pass

            times.append(t)
            S.append(S[-1])
            I.append(I[-1]-1)
            R.append(R[-1]+1)
        else: #transmit
            transmitter, recipient = IS_links[choice].choose_random() #we don't use remove since that complicates the later removal of edges.
            status[recipient] = 'I'
            
            infecteds.update(recipient, weight_increment = nodeweight(recipient))

            for uid, nbrData in H.neighbors[recipient].items():
                try:
                    IS_links[len(nbrData["neighbors"])+1].remove((nbrData["neighbors"], recipient)) # multiply by contagion?
                except:
                    pass

            for uid, nbrData in H.neighbors[recipient].items():
                for nbr in nbrData["neighbors"]:
                    if status[nbr] == 'S':
                        contagion = transmission_function(status, H.neighbors[nbr][uid]["neighbors"], **args)
                        if contagion != 0:
                            IS_links[len(nbrData["neighbors"])+1].update((H.neighbors[nbr][uid]["neighbors"], nbr), weight_increment = edgeweight(nbrData))

            times.append(t)
            S.append(S[-1]-1)
            I.append(I[-1]+1)
            R.append(R[-1])

        total_rates[1] = gamma*infecteds.total_weight()#I_weight_sum
        for size in H.getHyperedgeSizes():
            total_rates[size] = tau[size]*IS_links[size].total_weight() #IS_weight_sum

        total_rate = sum(total_rates.values())
        if total_rate>0:
            delay = random.expovariate(total_rate)
        else:
            delay = float('Inf')
        t += delay

    return np.array(times), np.array(S), np.array(I), np.array(R)
    
def Gillespie_SIS(H, tau, gamma, transmission_function=threshold, initial_infecteds=None, rho=None, tmin=0, tmax=100, recovery_weight=None, transmission_weight=None, **args):
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
            initial_number = int(round(H.number_of_nodes()*rho))
        initial_infecteds=random.sample(H.nodeLabels, initial_number)

    I = [len(initial_infecteds)]
    S = [H.number_of_nodes()-I[0]]
    times = [tmin]

    t = tmin
    transmissions = []

    status = defaultdict(lambda : 'S')
    for node in initial_infecteds:
        status[node] = 'I'

    if recovery_weight is None:
        infecteds = _ListDict_()
    else:
        infecteds = _ListDict_(weighted=True)

    IS_links = dict()
    for size in H.getHyperedgeSizes():
        if transmission_weight is None:
            IS_links[size] = _ListDict_()
        else:
            IS_links[size] = _ListDict_(weighted=True)

    for node in initial_infecteds:
        infecteds.update(node, weight_increment = nodeweight(node))
        for uid, nbrData in H.neighbors[node].items():  #must have this in a separate loop after assigning status of node
        # handle weighted vs. unweighted?
            for nbr in nbrData["neighbors"]: # there may be self-loops so account for this later
                if status[nbr] == 'S':
                    contagion = transmission_function(status, H.neighbors[nbr][uid]["neighbors"], **args)
                    if contagion != 0:
                        IS_links[len(nbrData["neighbors"])+1].update((H.neighbors[nbr][uid]["neighbors"], nbr), weight_increment=edgeweight(nbrData)) # need to be able to multiply by the contagion?

    total_rates = dict()
    total_rates[1] = gamma*infecteds.total_weight()#I_weight_sum
    for size in H.getHyperedgeSizes():
        total_rates[size] = tau[size]*IS_links[size].total_weight() #IS_weight_sum

    total_rate = sum(total_rates.values())

    delay = random.expovariate(total_rate)
    t += delay

    while infecteds and t < tmax:
        # rejection sampling
        while True:
            choice = random.choice(list(total_rates.keys()))
            if random.random() < total_rates[choice]/total_rate:
                break

        if choice == 1: #recover
            recovering_node = infecteds.random_removal() # chooses a node at random and removes it
            status[recovering_node] = 'S'

            # Find the SI links for the recovered node to get reinfected
            for uid, nbrData in H.neighbors[recovering_node].items():
                # if recipient in set(nbrData["neighbors"]):  #move past self edges
                #     continue
                # Not sure about this...
                contagion =  transmission_function(status, nbrData["neighbors"], **args)
                if contagion != 0:
                    IS_links[len(nbrData["neighbors"])+1].update((nbrData["neighbors"], recovering_node), weight_increment = edgeweight(nbrData))

            # reduce the number of infected links because of the healing
            for uid, nbrData in H.neighbors[recovering_node].items():
                for nbr in nbrData["neighbors"]:
                    if status[nbr] == 'S' and (H.neighbors[nbr][uid]["neighbors"], nbr) in IS_links[len(nbrData["neighbors"])+1]: # if the key doesn't exist, don't attempt to remove it
                        contagion = transmission_function(status, H.neighbors[nbr][uid]["neighbors"], **args)
                        if contagion == 0:
                            try:
                                IS_links[len(nbrData["neighbors"])+1].remove((H.neighbors[nbr][uid]["neighbors"], nbr)) # should this be "update" instead of "remove"?
                            except:
                                pass

            times.append(t)
            S.append(S[-1]+1)
            I.append(I[-1]-1)
        else:
            transmitter, recipient = IS_links[choice].choose_random()
            status[recipient]='I'

            infecteds.update(recipient, weight_increment = nodeweight(recipient))

            for uid, nbrData in H.neighbors[recipient].items():
                # if recipient in set(nbrData["neighbors"]):  #move past self edges
                #     continue
                # the above line messed up the simulation
                try:
                    IS_links[len(nbrData["neighbors"])+1].remove((nbrData["neighbors"], recipient)) # multiply by contagion?
                except:
                    pass

            for uid, nbrData in H.neighbors[recipient].items():
                for nbr in nbrData["neighbors"]:
                    if status[nbr] == 'S':
                        contagion = transmission_function(status, H.neighbors[nbr][uid]["neighbors"], **args)
                        if contagion != 0:
                            IS_links[len(nbrData["neighbors"])+1].update((H.neighbors[nbr][uid]["neighbors"], nbr), weight_increment = edgeweight(nbrData))
            times.append(t)
            S.append(S[-1]-1)
            I.append(I[-1]+1)

        total_rates[1] = gamma*infecteds.total_weight()
        for size in H.getHyperedgeSizes():
            total_rates[size] = tau[size]*IS_links[size].total_weight()
        total_rate = sum(total_rates.values())
        if total_rate > 0:
            delay = random.expovariate(total_rate)
        else:
            delay = float('Inf')
        t += delay
    return np.array(times), np.array(S), np.array(I)
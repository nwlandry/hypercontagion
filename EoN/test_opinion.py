import Hypergraph
import simulation
import matplotlib.pyplot as plt
#import networkx as nx
import time
import numpy as np
import opinion_simulation
import random

n = 1000
parameters = [{"degree-distribution":"uniform","min-degree":4,"max-degree":6,"hyperedge-size":2,"size":n,"is-correlated":True},{"degree-distribution":"uniform","min-degree":4,"max-degree":6,"hyperedge-size":3,"size":n,"is-correlated":True}]

# start = time.time()
# h = Hypergraph.HypergraphGenerator(parameters)
# G = Hypergraph.Hypergraph(h.getHyperedgeList())
# print(time.time() - start)

h = Hypergraph.HypergraphGenerator(parameters)
G = Hypergraph.Hypergraph(h.getHyperedges())

initial_states = np.random.uniform(low=-1.0, high=1.0, size=n)
yesAndNo = [random.choice(["Yes", "No"]) for i in range(n)]
yesAndNo = np.array(yesAndNo, dtype=object)
epsilon = 0.5
#t, states = opinion_simulation.random_group_sim_continuous_state_1D(G, initial_states, tmin = 0, tmax=10000, epsilon=epsilon)
# t, states = opinion_simulation.synchronous_update_continuous_state_1D(G, initial_states, tmin=0, tmax=20)
# plt.figure()
# plt.plot(t, states.T)
# plt.show()

#discrete state
t, states = opinion_simulation.random_node_and_group_sim_discrete_state(G, yesAndNo, tmin=0, tmax=10000)
yesArray = np.count_nonzero(states == "Yes", axis=0)
noArray = np.count_nonzero(states == "No", axis=0)
plt.figure()
plt.plot(t, yesArray)
plt.plot(t, noArray)
plt.show()

import Hypergraph
import simulation
import matplotlib.pyplot as plt
#import networkx as nx
import time
import numpy as np
import opinion_simulation
#import cProfile

n = 100
parameters = [{"degree-distribution":"uniform","min-degree":4,"max-degree":6,"hyperedge-size":2,"size":n,"is-correlated":True},{"degree-distribution":"uniform","min-degree":4,"max-degree":6,"hyperedge-size":10,"size":n,"is-correlated":True}]

# start = time.time()
# h = Hypergraph.HypergraphGenerator(parameters)
# G = Hypergraph.Hypergraph(h.getHyperedgeList())
# print(time.time() - start)

h = Hypergraph.HypergraphGenerator(parameters)
G = Hypergraph.Hypergraph(h.getHyperedges())

initial_states = np.random.uniform(low=-1.0, high=1.0, size=n)
initialFraction = 0.5
initial_states = np.random.choice([-1, 1], size=n, p=[1-initialFraction, initialFraction])
epsilon = 0.1
#t, states = opinion_simulation.random_group_sim_continuous_1D(G, initial_states, tmin = 0, tmax=100000, epsilon=epsilon)
t, states = opinion_simulation.synchronous_update_continuous_1D(G, initial_states, tmin=0, tmax=100)

plt.figure()
plt.plot(t, states.T)
plt.show()

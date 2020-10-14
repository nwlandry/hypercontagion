import Hypergraph
import simulation
import matplotlib.pyplot as plt
#import networkx as nx
import time
import numpy as np
import opinion_simulation
#import cProfile

n = 1000
parameters = [{"degree-distribution":"uniform","min-degree":4,"max-degree":6,"hyperedge-size":2,"size":n,"is-correlated":True},{"degree-distribution":"uniform","min-degree":4,"max-degree":6,"hyperedge-size":10,"size":n,"is-correlated":True}]

# start = time.time()
# h = Hypergraph.HypergraphGenerator(parameters)
# G = Hypergraph.Hypergraph(h.getHyperedgeList())
# print(time.time() - start)

h = Hypergraph.HypergraphGenerator(parameters)
G = Hypergraph.Hypergraph(h.getHyperedges())

initial_states = np.random.uniform(low=-1.0, high=1.0, size=n)
epsilon = 0.1
t, states = opinion_simulation.random_group_sim_continuous_1D(G, initial_states, tmin = 0, tmax=10000, epsilon=0.2)

plt.figure()
plt.plot(t, states.T)
plt.show()

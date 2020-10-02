import Hypergraph
import simulation
import matplotlib.pyplot as plt
#import networkx as nx
import time
import numpy as np
#import cProfile

n = 1000
parameters = [{"degree-distribution":"uniform","min-degree":4,"max-degree":6,"hyperedge-size":2,"size":n,"is-correlated":True},{"degree-distribution":"uniform","min-degree":4,"max-degree":6,"hyperedge-size":10,"size":n,"is-correlated":True}]

# start = time.time()
# h = Hypergraph.HypergraphGenerator(parameters)
# G = Hypergraph.Hypergraph(h.getHyperedgeList())
# print(time.time() - start)

start = time.time()
hDev = Hypergraph.HypergraphGeneratorDev(parameters)
GDev = Hypergraph.HypergraphDev(hDev.getHyperedges(), weightedEdges=True, nodeWeights=0.1*np.ones(1000))
print(time.time() - start)
initial_size = 10
gamma = 1.
tau = {2:0.6,10:0.2}
# start = time.time()
# t, S, I = simulation.Gillespie_SIS(G, tau, gamma, mechanism="collective", tmax = 200, initial_infecteds = range(initial_size))
# print(time.time() - start)

start = time.time()
#t, S, I = simulation.Gillespie_SIS(GDev, tau, gamma, tmax = 100, initial_infecteds = range(initial_size))
print(time.time() - start)

t, S, I, R = simulation.Gillespie_SIR(GDev, tau, gamma, tmax = 1000, initial_infecteds = range(initial_size), recovery_weight="weight", transmission_weight="weight")
plt.figure()
#plt.plot(t, S/n)
plt.plot(t, I)
#plt.plot(t, R/n)
plt.xlabel('time')
plt.ylabel('Fraction infected')
plt.show()

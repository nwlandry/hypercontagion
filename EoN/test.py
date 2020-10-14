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

h = Hypergraph.HypergraphGenerator(parameters)
G = Hypergraph.Hypergraph(h.getHyperedges(), weightedEdges=True, nodeWeights=np.ones(n)+np.random.rand(n))
initial_size = 10
gamma = 0.2
tau = {2:0.7,10:0.1}

t1, S1, I1, R1 = simulation.discrete_SIR(G, tau, gamma, tmin=0, tmax=1000, transmission_weight="weight", recovery_weight="weight", dt=0.1, initial_infecteds = range(initial_size))

t, S, I, R = simulation.Gillespie_SIR(G, tau, gamma, tmin=0, tmax = 1000, initial_infecteds = range(initial_size), recovery_weight="weight", transmission_weight="weight")
plt.figure()
plt.plot(t, S/n, label="S (continuous)")
plt.plot(t, I/n, label="I (continuous)")
plt.plot(t, R/n, label="R (continuous)")
plt.plot(t1, S1/n, label="S (discrete)")
plt.plot(t1, I1/n, label="I (discrete)")
plt.plot(t1, R1/n, label="R (discrete)")
plt.legend()
plt.xlabel('time')
plt.ylabel('Fraction infected')
plt.show()


t1, S1, I1 = simulation.discrete_SIS(G, tau, gamma, tmin=0, tmax=1000, transmission_weight="weight", recovery_weight="weight", dt=0.1, initial_infecteds = range(initial_size))
t, S, I = simulation.Gillespie_SIS(G, tau, gamma, tmin=0, tmax = 1000, transmission_weight="weight", recovery_weight="weight", initial_infecteds = range(initial_size))

plt.figure()
plt.plot(t, S/n, label="S (continuous)")
plt.plot(t, I/n, label="I (continuous)")
plt.plot(t1, S1/n, label="S (discrete)")
plt.plot(t1, I1/n, label="I (discrete)")
plt.legend()
plt.xlabel('time')
plt.ylabel('Fraction infected')
plt.show()

import Hypergraph
import simulation
import matplotlib.pyplot as plt
#import networkx as nx
import time
import numpy as np
#import cProfile

n = 1000
parameters = [{"degree-distribution":"power-law","min-degree":10,"max-degree":1000,"hyperedge-size":2,"size":n,"is-correlated":True,"exponent":3},{"degree-distribution":"power-law","min-degree":10,"max-degree":1000,"hyperedge-size":3,"size":n,"is-correlated":True,"exponent":3}]

h = Hypergraph.HypergraphGenerator(parameters)
G = Hypergraph.Hypergraph(h.getHyperedges())
initial_size = 10
gamma = 2
tau = {2:.1,3:0}
#
start = time.time()
t1, S1, I1, R1 = simulation.discrete_SIR(G, tau, gamma, tmin=0, tmax=1000, dt=0.001, initial_infecteds = range(initial_size))
print(time.time() - start)

start = time.time()
t, S, I, R = simulation.Gillespie_SIR(G, tau, gamma, tmin=0, tmax = 1000, initial_infecteds = range(initial_size))
print(time.time() - start)

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
# #
# start = time.time()
# t1, S1, I1 = simulation.discrete_SIS(G, tau, gamma, tmin=0, tmax=10, dt=0.1, initial_infecteds = range(initial_size))
# print(time.time() - start)
#
# start = time.time()
# t, S, I = simulation.Gillespie_SIS(G, tau, gamma, tmin=0, tmax = 10, initial_infecteds = range(initial_size))
# print(time.time() - start)
#
# plt.figure()
# plt.plot(t, S/n, label="S (continuous)")
# plt.plot(t, I/n, label="I (continuous)")
# plt.plot(t1, S1/n, label="S (discrete)")
# plt.plot(t1, I1/n, label="I (discrete)")
# plt.legend()
# plt.xlabel('time')
# plt.ylabel('Fraction infected')
# plt.show()

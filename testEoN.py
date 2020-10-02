from __future__ import absolute_import
import networkx as nx
import EoN
import matplotlib.pyplot as plt
import time

G = nx.configuration_model([1,5,10]*10000)
initial_size = 1000
gamma = 1.
tau = 0.2
start = time.time()
t, S, I = EoN.Gillespie_SIS(G, tau, gamma, tmax = 20, initial_infecteds = range(initial_size))
print(time.time() - start)

plt.figure()
plt.plot(t, I)
plt.xlabel('time')
plt.ylabel('Fraction infected')
plt.show()

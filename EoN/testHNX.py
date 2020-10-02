import Hypergraph
import simulation
import hypernetx as hnx

n = 1000
parameters = [{"degree-distribution":"uniform","min-degree":4,"max-degree":6,"hyperedge-size":2,"size":n,"is-correlated":True},{"degree-distribution":"uniform","min-degree":4,"max-degree":6,"hyperedge-size":3,"size":n,"is-correlated":True}]

h = Hypergraph.HypergraphGeneratorDev(parameters)
H = hnx.Hypergraph(h.getHyperedgeList())
print(Stop)
print(h.getHyperedgeList())
print(H.neighbors(6))
for nbr in H.neighbors(6):
    print(nbr)
print(stop)
initial_size = 1000
gamma = 1.
tau = {2:0.2,3:0.2}

t, S, I = simulation.Gillespie_SIS(G, tau, gamma, tmax = 20, initial_infecteds = range(initial_size))

#t, S, I, R = simulation.Gillespie_SIS(G, tau, gamma, tmax = 1000, initial_infecteds = range(initial_size))
# plt.figure()
# #plt.plot(t, S/n)
# plt.plot(t, I)
# #plt.plot(t, R/n)
# plt.xlabel('time')
# plt.ylabel('Fraction infected')
# plt.show()

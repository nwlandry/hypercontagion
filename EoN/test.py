import Hypergraph


parameters = [{"degree-distribution":"uniform","min-degree":10,"max-degree":1000,"hyperedge-size":2,"size":100,"is-correlated":True}]

h = Hypergraph.HypergraphGenerator(parameters)
hypergraph = Hypergraph.Hypergraph(h.getHyperedgeList(), False)
print(hypergraph.neighborList)

import random
import time
from collections import defaultdict

class Hypergraph:
    def __init__(self, hyperedges, weightedEdges=False):
        self.addEdges(hyperedges, weightedEdges)
        self.deleteDegenerateHyperedges()
        self.findHyperedgeSizes()
        self.generateNeighbors()
        self.nodeLabels = list(self.nodes.keys())

    def __iter__(self):
        """Iterate over the nodes. Use: 'for n in G'.
        Returns
        -------
        niter : iterator
            An iterator over all nodes in the graph.
        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> [n for n in G]
        [0, 1, 2, 3]
        >>> list(G)
        [0, 1, 2, 3]
        """
        return iter(self.nodes)

    def __contains__(self, n):
        """Returns True if n is a node, False otherwise. Use: 'n in G'.
        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> 1 in G
        True
        """
        try:
            return n in self.nodes
        except TypeError:
            return False

    def __len__(self):
        """Returns the number of nodes in the graph. Use: 'len(G)'.
        Returns
        -------
        nnodes : int
            The number of nodes in the graph.
        See Also
        --------
        number_of_nodes, order  which are identical
        Examples
        --------
        >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> len(G)
        4
        """
        return len(self.nodes)

    def addEdges(self, hyperedges, weightedEdges):
        # unweighted format for hyperedges: {"id0":{"members":(1,2,3)}, "id1":{"members":(1,2)},...}
        # weighted format for hyperedges: {"id0":{"members":(1,2,3),"weight":1.1}, "id1":{"members":(1,2),"weight":0.5},...}
        self.weightedEdges = weightedEdges
        self.nodes = dict()
        nodes = set()
        # if list of tuples
        if isinstance(hyperedges, list):
            self.hyperedges = dict()
            uid = 0
            for hyperedge in hyperedges:
                if self.weightedEdges:
                    self.hyperedges[uid] = {"members":hyperedge[:-1],"weight":hyperedge[-1]}
                else:
                    self.hyperedges[uid] = {"members":hyperedge}
                    nodes.update(hyperedge)

        elif isinstance(hyperedges, dict):
            self.hyperedges = hyperedges.copy()
            for edgeData in self.hyperedges.values():
                nodes.update(edgeData["members"])

        for nodeLabel in list(nodes):
            self.nodes[nodeLabel] = dict()

    def addNodeAttributes(self, nodeAttributes):
        # find unique nodes in the hyperedges
        for label, attribute in nodeAttributes.items():
            try:
                self.nodes[label] = attribute
            except:
                print("invalid label")

    def deleteDegenerateHyperedges(self):
        cleanedHyperedges = dict()
        for uid, hyperedge in self.hyperedges.items():
            if len(hyperedge["members"]) >= 2:
                cleanedHyperedges[uid] = hyperedge
        self.hyperedges = cleanedHyperedges

    def number_of_nodes(self):
        return len(self.nodes)

    def has_node(self, n):
        try:
            return n in self.nodes
        except TypeError:
            return False

    def findHyperedgeSizes(self):
        hyperedgeSizes = set()
        for edgeData in list(self.hyperedges.values()):
            hyperedgeSizes.add(len(edgeData["members"]))
        self.hyperedgeSizes = list(hyperedgeSizes)

    def getHyperedgeSizes(self):
        return self.hyperedgeSizes

    def generateNeighbors(self):
        self.neighbors = dict()
        if self.weightedEdges:
            self.generateWeightedNeighbors()
        else:
            self.generateUnweightedNeighbors()

    def generateUnweightedNeighbors(self):
        for uid, edgeData in self.hyperedges.items():
            try:
                members = edgeData["members"]
            except:
                print("Incorrect input format for hyperedge list")
                break
            for index in range(len(members)):
                try:
                    self.neighbors[members[index]][uid] = {"neighbors":tuple([members[i] for i in range(len(members)) if i != index])}
                except:
                    self.neighbors[members[index]] = {uid:{"neighbors":tuple([members[i] for i in range(len(members)) if i != index])}}

    def generateWeightedNeighbors(self):
        print(self.hyperedges)
        for uid, edgeData in self.hyperedges.items():
            try:
                members = edgeData["members"]
                weight = edgeData["weight"]
            except:
                print("Incorrect input format for weighted hyperedge list")
                break
            for index in range(len(members)):
                try:
                    print(members[index])
                    self.neighbors[members[index]][uid] = {"neighbors":tuple([members[i] for i in range(len(members)) if i != index]), "weight":weight}
                except:
                    self.neighbors[members[index]] = {uid:{"neighbors":tuple([members[i] for i in range(len(members)) if i != index]), "weight":weight}}

class HypergraphGenerator:
    def __init__(self, structure):
        self.generateHyperdegreeSequence(structure)
        self.generateHyperedges()

    def getHyperedges(self):
        return self.hyperedges

    def getHyperdegreeSequence(self):
        return self.hyperdegreeSequence

    def generateHyperdegreeSequence(self, structure):
        self.hyperdegreeSequence = dict()
        correlatedSequence = list()
        for info in structure:
            try:
                hyperedgeSize = info["hyperedge-size"]
            except:
                print("Error in specified distribution parameters")

            if info["degree-distribution"] == "power-law":
                try:
                    numNodes = info["size"]
                    minDegree = info["min-degree"]
                    maxDegree = info["max-degree"]
                    exponent = info["exponent"]
                except:
                    print("Error in specified distribution parameters")
                    break
                sequence = self.generatePowerLawDegreeSequence(numNodes, minDegree, maxDegree, exponent)
            elif info["degree-distribution"] == "uniform":
                try:
                    numNodes = info["size"]
                    minDegree = info["min-degree"]
                    maxDegree = info["max-degree"]
                except:
                    print("Error in specified distribution parameters")
                    break
                sequence = self.generateUniformDegreeSequence(numNodes, minDegree, maxDegree)
            elif info["degree-distribution"] == "poisson":
                try:
                    numNodes = info["size"]
                    meanDegree = info["mean-degree"]
                except:
                    print("Error in specified distribution parameters")
                    break
                sequence = self.generatePoissonDegreeSequence(numNodes, meanDegree)
            else:
                print("Invalid selection")
                break
            try:
                isCorrelated = info["is-correlated"]
            except:
                print("Specify whether this hyperedge size is correlated or not")
                break
            if isCorrelated:
                if correlatedSequence == []:
                    correlatedSequence = sequence
                self.hyperdegreeSequence[hyperedgeSize] = correlatedSequence
            else:
                self.hyperdegreeSequence[hyperedgeSize] = sequence

    def generateHyperedges(self):
        self.hyperedges = dict()
        for hyperedgeSize, degreeSequence in self.hyperdegreeSequence.items():
            self.hyperedges.update(self.generateHyperedgesBySize(hyperedgeSize, degreeSequence))

    def generateHyperedgesBySize(self, hyperedgeSize, degreeSequence, weighted=True):
        import string
        k = degreeSequence.copy()
        # Making sure we have the right number of stubs
        if (sum(k) % hyperedgeSize) != 0:
            remainder = sum(k) % hyperedgeSize
            for i in range(int(round(hyperedgeSize - remainder))):
                j = random.randrange(len(k))
                k[j] = k[j] + 1

        stubs = list()
        hyperedges = dict()
        # Creating the list to index through
        for index in range(len(k)):
            stubs.extend([index]*int(k[index]))

        while len(stubs) != 0:
            uid = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
            u = random.sample(range(len(stubs)), hyperedgeSize)
            hyperedge = list()
            for index in u:
                hyperedge.append(stubs[index])
            if weighted:
                hyperedges[uid] = {"members":tuple(hyperedge),"weight":random.random()}
            else:
                hyperedges[uid] = {"members":tuple(hyperedge)}
            # add weighted option?

            for index in sorted(u, reverse=True):
                del stubs[index]
        return hyperedges

    def generatePowerLawDegreeSequence(self, numNodes, minDegree, maxDegree, exponent):
        degreeSequence = list()
        for i in range(numNodes):
            u = random.uniform(0, 1)
            degreeSequence.append(round(self.invCDFPowerLaw(u, minDegree, maxDegree, exponent)))
        return degreeSequence # originally this was sorted but I'm worried about between-size correlations

    def invCDFPowerLaw(self, u, minDegree, maxDegree, exponent):
        return (minDegree**(1-exponent) + u*(maxDegree**(1-exponent) - minDegree**(1-exponent)))**(1/(1-exponent))

    def generateUniformDegreeSequence(self, numNodes, minDegree, maxDegree):
        degreeSequence = list()
        for i in range(numNodes):
            u = random.randrange(round(minDegree), round(maxDegree))
            degreeSequence.append(round(u))
        return degreeSequence

    def generatePoissonDegreeSequence(self, numNodes, meanDegree):
        return np.random.poisson(lam=meanDegree, size=numNodes).tolist()

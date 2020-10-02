import random
import time

class Hypergraph:
    def __init__(self, hyperedgeList, isWeighted=False, nodeWeights=None):
        self.importHyperedges(hyperedgeList, isWeighted)
        self.deleteDegenerateHyperedges()
        self.computeHypergraphSize()
        self.findHyperedgeSizes()
        self.importNodeWeights(nodeWeights)
        self.createNeighborList()
        self.createNodeList(nodeWeights)

    def importHyperedges(self, hyperedgeList, isWeighted):
        # unweighted format for hyperedges: {"id0":{"edge":(1,2,3)}, "id1":{"edge":(1,2)},...}
        # weighted format for hyperedges: {"id0":{"edge":(1,2,3),"weight":1.1}, "id1":{"edge":(1,2),"weight":0.5},...}
        self.hyperedges = hyperedgeList.copy()
        self.isWeighted = isWeighted
        # need a better way to check whether the format is correct

    def importNodeWeights(self, nodeWeights):
        if nodeWeights == None:
            self.weightedNodes = False
            self.nodes = dict()
            for i in range(self.numNodes):
                self.nodes[i] = dict()
        else:
            self.weightedNodes = True
            self.nodes = dict()
            for i in range(self.numNodes):
                self.nodes[i] = nodeWeights[i]

    def deleteDegenerateHyperedges(self):
        cleanedHyperedges = list()
        for hyperedge in self.hyperedges:
            if len(hyperedge) >= 2:
                cleanedHyperedges.append(hyperedge)
        self.hyperedges = cleanedHyperedges

    def sortHyperedgeListBySize(self):
        self.hyperedges.sort(key = len)

    def createNodeList(self, nodeWeights):
        self.nodes = dict()
        if nodeWeights != None:
            for i in range(len(nodeWeights)):
                self.nodes[i] = {"weight":nodeWeights[i]}
            if self.numNodes != len(self.nodes.keys()):
                raise Exception("Not the same length")
        else:
            for i in range(self.numNodes):
                self.nodes[i] = dict()

    # Possibly a better way to do this is to store the max and min indices
    def computeHypergraphSize(self):
        minIndex = min([min(hyperedge) for hyperedge in self.hyperedges])
        maxIndex = max([max(hyperedge) for hyperedge in self.hyperedges])
        self.numNodes = maxIndex - minIndex + 1
        # return max and min indices?

    def order(self):
        try:
            return self.numNodes
        except:
            self.computeHypergraphSize()
            return self.numNodes

    def has_node(self, nodeList):
        # Implement later
        return True

    def findHyperedgeSizes(self):
        self.hyperedgeSizes = list(set(map(len, self.hyperedges)))

    def getHyperedgeSizes(self):
        try:
            return self.hyperedgeSizes
        except:
            self.findHyperedgeSizes()
            return self.hyperedgeSizes

    def neighbors(self, node):
        return self.neighborList[node]

    def createNeighborList(self):
        self.neighborList = dict()
        if self.isWeighted:
            self.createWeightedNeighborList()
        else:
            self.createUnWeightedNeighborList()

    def createUnWeightedNeighborList(self):
        for hyperedge in self.hyperedges:
            for index in range(len(hyperedge)):
                try:
                    self.neighborList[hyperedge[index]].append([hyperedge[i] for i in range(len(hyperedge)) if i != index])
                except:
                    self.neighborList[hyperedge[index]] = [[hyperedge[i] for i in range(len(hyperedge)) if i != index]]

    def createWeightedNeighborList(self):
        for item in self.hyperedges:
            try:
                hyperedge = item["members"]
                weight = item["weight"]
            except:
                print("Incorrect input format for weighted hyperedge list")
                break
            for index in range(len(hyperedge)):
                try:
                    self.neighborList[hyperedge[index]].append({"neighbors":[hyperedge[i] for i in range(len(hyperedge)) if i != index], "weight":weight})
                except:
                    self.neighborList[hyperedge[index]] = {len(hyperedge):[{"neighbors":[hyperedge[i] for i in range(len(hyperedge)) if i != index], "weight":weight}]}

class HypergraphDev:
    def __init__(self, hyperedges, weightedEdges=False, nodeWeights=None):
        self.importHyperedges(hyperedges, weightedEdges)
        self.deleteDegenerateHyperedges()
        self.generateNodes(nodeWeights)
        self.computeHypergraphSize()
        self.findHyperedgeSizes()
        self.generateNeighbors()

    def importHyperedges(self, hyperedges, weightedEdges):
        # unweighted format for hyperedges: {"id0":{"edge":(1,2,3)}, "id1":{"edge":(1,2)},...}
        # weighted format for hyperedges: {"id0":{"edge":(1,2,3),"weight":1.1}, "id1":{"edge":(1,2),"weight":0.5},...}
        self.hyperedges = hyperedges.copy()
        self.weightedEdges = weightedEdges
        # need a better way to check whether the format is correct

    def generateNodes(self, nodeWeights):
        nodes = set()
        for edgeData in self.hyperedges.values():
            nodes.update(edgeData["edge"])

        if nodeWeights is None:
            self.weightedNodes = False
            self.nodes = dict()
            for nodeLabel in list(nodes):
                self.nodes[nodeLabel] = dict()
        else:
            self.weightedNodes = True
            self.nodes = dict()
            if len(nodes) != len(nodeWeights):
                raise Exception("Not the same length")
            for nodeLabel in list(nodes):
                self.nodes[nodeLabel] = {"weight":nodeWeights[nodeLabel]}


    def deleteDegenerateHyperedges(self):
        cleanedHyperedges = dict()
        for uid, hyperedge in self.hyperedges.items():
            if len(hyperedge["edge"]) >= 2:
                cleanedHyperedges[uid] = hyperedge
        self.hyperedges = cleanedHyperedges

    # Possibly a better way to do this is to store the max and min indices
    def computeHypergraphSize(self):
        # minIndex = min([min(hyperedge) for hyperedge in list(self.hyperedges.values())])
        # maxIndex = max([max(hyperedge) for hyperedge in list(self.hyperedges.values())])
        # self.numNodes = maxIndex - minIndex + 1
        self.numNodes = len(self.nodes)
        # return max and min indices?

    def order(self):
        try:
            return self.numNodes
        except:
            self.computeHypergraphSize()
            return self.numNodes

    def has_node(self, nodeList):
        # Implement later
        return True

    def findHyperedgeSizes(self):
        hyperedgeSizes = set()
        for edgeData in list(self.hyperedges.values()):
            hyperedgeSizes.add(len(edgeData["edge"]))
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
            for index in range(len(edgeData["edge"])):
                try:
                    self.neighbors[edgeData["edge"][index]][uid] = {"neighbors":tuple([edgeData["edge"][i] for i in range(len(edgeData["edge"])) if i != index])}
                except:
                    self.neighbors[edgeData["edge"][index]] = {uid:{"neighbors":tuple([edgeData["edge"][i] for i in range(len(edgeData["edge"])) if i != index])}}

    def generateWeightedNeighbors(self):
        for uid, item in self.hyperedges.items():
            try:
                hyperedge = item["edge"]
                weight = item["weight"]
            except:
                print("Incorrect input format for weighted hyperedge list")
                break
            for index in range(len(hyperedge)):
                try:
                    self.neighbors[hyperedge[index]][uid] = {"neighbors":tuple([hyperedge[i] for i in range(len(hyperedge)) if i != index]), "weight":weight}
                except:
                    self.neighbors[hyperedge[index]] = {uid:{"neighbors":tuple([hyperedge[i] for i in range(len(hyperedge)) if i != index]), "weight":weight}}

class HypergraphGenerator:
    def __init__(self, structure):
        self.generateHyperdegreeSequence(structure)
        self.generateHyperedges()

    def getHyperedgeList(self):
        return self.hyperedgeList

    def getHyperdegreeSequence(self):
        return self.hyperdegreeSequence

    def generateHyperdegreeSequence(self, structure):
        self.hyperdegreeSequence = dict()
        correlatedSequence = list()
        for info in structure:
            try:
                hyperedgeSize = info["hyperedge-size"]
            except:
                print("Error in specified parameters")

            if info["degree-distribution"] == "power-law":
                try:
                    numNodes = info["size"]
                    minDegree = info["min-degree"]
                    maxDegree = info["max-degree"]
                    exponent = info["exponent"]
                except:
                    print("Error in specified parameters")
                    break
                sequence = self.generatePowerLawDegreeSequence(numNodes, minDegree, maxDegree, exponent)
            elif info["degree-distribution"] == "uniform":
                try:
                    numNodes = info["size"]
                    minDegree = info["min-degree"]
                    maxDegree = info["max-degree"]
                except:
                    print("Error in specified parameters")
                    break
                sequence = self.generateUniformDegreeSequence(numNodes, minDegree, maxDegree)
            elif info["degree-distribution"] == "poisson":
                try:
                    numNodes = info["size"]
                    meanDegree = info["mean-degree"]
                except:
                    print("Error in specified parameters")
                    break
                sequence = self.generatePoissonDegreeSequence(numNodes, meanDegree)
            else:
                print("Invalid selection")
                break
            try:
                isCorrelated = info["is-correlated"]
            except:
                print("Specify whether this layer is correlated or not")
                break
            if isCorrelated:
                if correlatedSequence == []:
                    correlatedSequence = sequence
                self.hyperdegreeSequence[hyperedgeSize] = correlatedSequence
            else:
                self.hyperdegreeSequence[hyperedgeSize] = sequence

    def generateHyperedges(self):
        self.hyperedgeList = list()
        for hyperedgeSize, degreeSequence in self.hyperdegreeSequence.items():
            self.hyperedgeList += self.generateHyperedgesBySize(hyperedgeSize, degreeSequence)

    def generateHyperedgesBySize(self, hyperedgeSize, degreeSequence):
        k = degreeSequence.copy()
        # Making sure we have the right number of stubs
        if (sum(k) % hyperedgeSize) != 0:
            remainder = sum(k) % hyperedgeSize
            for i in range(int(round(hyperedgeSize - remainder))):
                j = random.randrange(len(k))
                k[j] = k[j] + 1

        stubs = list()
        hyperedgeList = list()
        # Creating the list to index through
        for index in range(len(k)):
            stubs.extend([index]*int(k[index]))

        while len(stubs) != 0:
            u = random.sample(range(len(stubs)), hyperedgeSize)
            hyperedge = list()
            for index in u:
                hyperedge.append(stubs[index])
            hyperedgeList.append(hyperedge)

            for index in sorted(u, reverse=True):
                del stubs[index]
        return hyperedgeList

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

class HypergraphGeneratorDev:
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
                print("Error in specified parameters")

            if info["degree-distribution"] == "power-law":
                try:
                    numNodes = info["size"]
                    minDegree = info["min-degree"]
                    maxDegree = info["max-degree"]
                    exponent = info["exponent"]
                except:
                    print("Error in specified parameters")
                    break
                sequence = self.generatePowerLawDegreeSequence(numNodes, minDegree, maxDegree, exponent)
            elif info["degree-distribution"] == "uniform":
                try:
                    numNodes = info["size"]
                    minDegree = info["min-degree"]
                    maxDegree = info["max-degree"]
                except:
                    print("Error in specified parameters")
                    break
                sequence = self.generateUniformDegreeSequence(numNodes, minDegree, maxDegree)
            elif info["degree-distribution"] == "poisson":
                try:
                    numNodes = info["size"]
                    meanDegree = info["mean-degree"]
                except:
                    print("Error in specified parameters")
                    break
                sequence = self.generatePoissonDegreeSequence(numNodes, meanDegree)
            else:
                print("Invalid selection")
                break
            try:
                isCorrelated = info["is-correlated"]
            except:
                print("Specify whether this layer is correlated or not")
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
                hyperedges[uid] = {"edge":tuple(hyperedge),"weight":random.random()}
            else:
                hyperedges[uid] = {"edge":tuple(hyperedge)}
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

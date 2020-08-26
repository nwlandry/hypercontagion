import random
import time

class Hypergraph:
    def __init__(self, hyperedgeList, isWeighted=False, hyperedgeWeights=None, nodeWeights=None):
        self.importHyperedgeList(hyperedgeList, isWeighted)
        self.deleteDegenerateHyperedges()
        self.sortHyperedgeListBySize()
        self.computeHypergraphSize()
        self.findHyperedgeSizes()
        self.createNeighborList()

    def importHyperedgeList(self, hyperedgeList, isWeighted):
        self.hyperedgeList = hyperedgeList.copy()
        self.isWeighted = isWeighted
        # need a better way to check whether the format is correct

    def deleteDegenerateHyperedges(self):
        cleanedHyperedges = list()
        for hyperedge in self.hyperedgeList:
            if len(hyperedge) >= 2:
                cleanedHyperedges.append(hyperedge)
        self.hyperedgeList = cleanedHyperedges

    def sortHyperedgeListBySize(self):
        self.hyperedgeList.sort(key = len)

    # Possibly a better way to do this is to store the max and min indices
    def computeHypergraphSize(self):
        maxIndex = 0
        for hyperedge in self.hyperedgeList:
            if maxIndex < max(hyperedge):
                maxIndex = max(hyperedge)
        self.numNodes = maxIndex + 1 # Assuming 0 indexing, maybe do away with this in the future?

    def order():
        try:
            return self.numNodes
        except:
            self.computeHypergraphSize()
            return self.numNodes

    def has_node(nodeList):
        # Implement later
        return True

    def findHyperedgeSizes(self):
        self.hyperedgeSizes = list(set(map(len, self.hyperedgeList)))

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
        for hyperedge in self.hyperedgeList:
            for index in range(len(hyperedge)):
                try:
                    self.neighborList[hyperedge[index]].append([hyperedge[i] for i in range(len(hyperedge)) if i != index])
                except:
                    self.neighborList[hyperedge[index]] = [[hyperedge[i] for i in range(len(hyperedge)) if i != index]]

    def createWeightedNeighborList(self):
        for item in self.hyperedgeList:
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

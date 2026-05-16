# -*- coding: utf-8 -*-


class DataModel:
    """
    this class contains all the data structures needed by the various
    components. The same data model can be used for both command line and GUI
    interfaces
    """

    def __init__(self):
        self.dataset = None
        self.tokenizedDataset = None
        self.tokenSet = None
        self.numberOfPoints = 0
        self.numberOfUniquePoints = 0
        self.numberOfClusters = 0
        self.pointGraph = None
        self.similarityGraph = None
        self.semanticGraph = None
        self.pointTokens = None
        self.numberOfTokens = 0
        self.numberOfTokensNoDigits = 0
        self.leafNodes = None
        self.unclusteredPoints = []
        self.labeledDataset = None
        self.supportedClassLabels = []
        self.supportedPointLabels = []  # 오타 수정: 누락되었던 point labels 초기화 추가

    """ getters and setters """
    @property
    def dataset(self):
        return self.__dataset

    @dataset.setter
    def dataset(self, dataset):
        self.__dataset = dataset

    @property
    def tokenizedDataset(self):
        return self.__tokenizedDataset

    @tokenizedDataset.setter
    def tokenizedDataset(self, tokenizedDataset):
        self.__tokenizedDataset = tokenizedDataset

    @property
    def tokenSet(self):
        return self.__tokenSet

    @tokenSet.setter
    def tokenSet(self, tokenSet):
        self.__tokenSet = tokenSet

    @property
    def numberOfUniquePoints(self):
        return self.__numberOfUniquePoints

    @numberOfUniquePoints.setter
    def numberOfUniquePoints(self, number):
        self.__numberOfUniquePoints = number

    @property
    def numberOfClusters(self):
        return self.__numberOfClusters

    @numberOfClusters.setter
    def numberOfClusters(self, number):
        self.__numberOfClusters = number

    @property
    def semanticGraph(self):
        return self.__semanticGraph

    @semanticGraph.setter
    def semanticGraph(self, graph):
        self.__semanticGraph = graph

    @property
    def similarityGraph(self):
        return self.__similarityGraph

    @similarityGraph.setter
    def similarityGraph(self, graph):
        self.__similarityGraph = graph

    @property
    def pointGraph(self):
        return self.__pointGraph

    @pointGraph.setter
    def pointGraph(self, pointGraph):
        self.__pointGraph = pointGraph

    @property
    def pointTokens(self):
        return self.__pointTokens

    @pointTokens.setter
    def pointTokens(self, pointTokens):
        self.__pointTokens = pointTokens

    @property
    def numberOfTokens(self):
        return self.__numberOfTokens

    @numberOfTokens.setter
    def numberOfTokens(self, numberOfTokens):
        self.__numberOfTokens = numberOfTokens

    @property
    def numberOfTokensNoDigits(self):
        return self.__numberOfTokensNoDigits

    @numberOfTokensNoDigits.setter
    def numberOfTokensNoDigits(self, numberOfTokensNoDigits):
        self.__numberOfTokensNoDigits = numberOfTokensNoDigits

    @property
    def leafNodes(self):
        return self.__leafNodes

    @leafNodes.setter
    def leafNodes(self, leafNodes):
        self.__leafNodes = leafNodes

    @property
    def unclusteredPoints(self):
        return self.__unclusteredPoints

    @unclusteredPoints.setter
    def unclusteredPoints(self, unclusteredPoints):
        self.__unclusteredPoints = unclusteredPoints

    @property
    def labeledDataset(self):
        return self.__labeledDataset

    @labeledDataset.setter
    def labeledDataset(self, labeledDataset):
        self.__labeledDataset = labeledDataset

    @property
    def supportedClassLabels(self):
        return self.__supportedClassLabels

    @supportedClassLabels.setter
    def supportedClassLabels(self, labels):
        self.__supportedClassLabels = labels

    @property
    def supportedPointLabels(self):
        return self.__supportedPointLabels

    @supportedPointLabels.setter
    def supportedPointLabels(self, labels):
        self.__supportedPointLabels = labels
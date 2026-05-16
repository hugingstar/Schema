# -*- coding: utf-8 -*-

import sys
import logging
from collections import deque

import pandas as pd

from inference.configuration.configuration import CONFIG
from inference.classifier.Constants import CONSTANTS
from inference.graphs.PointGraph import PointGraph
from inference.graphs.SemanticGraph import SemanticGraph
from inference.graphs.SimilarityGraph import SimilarityGraph

from inference.tokens.SimpleTokenizer import SimpleTokenizer
from inference.tokens.PointTokens import PointTokens
from inference.classifier.SemanticInferor import SemanticInferor
from dataset.utc.utilities.DatasetParser import DatasetParser
from dataset.utc.utilities.Dataset import Dataset


class InferenceManager:
    """
    this class oversees the creation of a semantic model out of point names
    """
    def __init__(self, dataModel):
        # Python 3 대응: 로거 식별명 규칙 최적화
        self.__logger = logging.getLogger(__name__)
        self.__logger.info('initialization')
        if dataModel is None:
            self.__logger.error('dataModel needs to be instantiated first')
            sys.exit(0)
        self.__dataModel = dataModel
        self.__instantiateGraphs()
        
    @property
    def semanticGraph(self):
        return self.__semanticGraph

    @semanticGraph.setter
    def semanticGraph(self, semanticGraph):
        self.__semanticGraph = semanticGraph

    @property
    def similarityGraph(self):
        return self.__similarityGraph

    @similarityGraph.setter
    def similarityGraph(self, similarityGraph):
        self.__similarityGraph = similarityGraph

    @property
    def pointGraph(self):
        return self.__pointGraph

    @pointGraph.setter
    def pointGraph(self, pointGraph):
        self.__pointGraph = pointGraph

    def __instantiateGraphs(self):
        self.pointGraph = PointGraph(
                classGuesserType=CONFIG.CLASSNAMEGUESSER)
        self.similarityGraph = SimilarityGraph(self.pointGraph,
                                      classGuesserType=CONFIG.CLASSNAMEGUESSER)
        self.semanticGraph = SemanticGraph(self.pointGraph,
                                           self.similarityGraph,
                                           classGuesserType=CONFIG.CLASSNAMEGUESSER)
        self.__inferor = SemanticInferor(self.semanticGraph)
        dataModel = self.__dataModel
        dataModel.supportedPointLabels = self.__inferor.supportedPointLabels
        dataModel.supportedClassLabels = self.__inferor.supportedClassLabels

    def loadDatasetFromFile(self, filename):
        """
        load a dataset from file
        """
        dataset = Dataset()
        self.__dataModel.dataset = dataset
        return dataset.loadDatasetFromFile(filename)

    def loadDatasetFromDB(self, datasetID):
        """
        load a dataset from DB
        """
        datasetParser = DatasetParser()
        dataset = datasetParser.loadBACnetNetworkPointDB(datasetID)
        self.__dataModel.dataset = dataset
        return True, ''

    def tokenizeDataset(self):
        """
        tokenize the dataset
        """
        self.__logger.info('start to tokenize...')
        if self.__dataModel.dataset is None:
            msg = 'Dataset is not initialized, \ndataset must be loaded before start to tokenize'
            self.__logger.error(msg)
            return False, msg
        pointTokens = self.__convertListOfPointsInListOfPointTokens(self.__dataModel.dataset)
        tokenizer = SimpleTokenizer()
        tokenizedDataset = tokenizer.tokenizePointList(pointTokens)
        tokenizer.normalizeTokens()

        self.__dataModel.tokenizedDataset = tokenizedDataset
        self.__dataModel.tokenSet = tokenizer.tokenSet
        msg = 'tokenization completed'
        self.__logger.info(msg)
        return True, msg

    def inferSemanticModel(self):
        """
        this method oversees the sequence of operations taken to infer the semantics from point names
        """
        tokenizedDataset = self.__dataModel.tokenizedDataset
        # 하위 호환성 필드 획득 조치
        datasetID = getattr(self.__dataModel.dataset, 'dataset_name', getattr(self.__dataModel.dataset, 'datasetName', None))
        
        # 호출 버그 대응을 위해 내부 파라미터 전달 유지
        self.cluster(tokenizedDataset, datasetID)
        self.classifyClusters()

    def classifyClusters(self):
        """
        attempts to classify clusters of points into equipments
        """
        semGraph = self.semanticGraph
        datasetName = self.__dataModel.dataset.datasetName
        leafNodes = self.__dataModel.leafNodes
        if self.__dataModel.dataset is None:
            msg = 'Dataset is not initialized, \ndataset must be loaded before start to classify clusters'
            self.__logger.error(msg)
            return False, msg
        if self.semanticGraph.graph is None:
            msg = 'before classifying clusters, clusterize points'
            self.__logger.error(msg)
            return False, msg

        tokenSetOfClasses = semGraph.getTokenSetOfClasses()
        self.__logger.error('starting to classify clusters')
        self.__inferor.classifyClusters(tokenSetOfClasses)
        semGraph.reportOnBaseClassesUsage()
        semGraph.getSummaryOfClasses()
        semGraph.saveTokenSetOfClasses(tokenSetOfClasses, None, datasetName)
        self.similarityGraph.printReportOnSimilarityGraph(leafNodes)
        semGraph.saveSemanticGraphImage(tokenSetOfClasses)

        msg = 'classification of clusters completed'
        self.__logger.info(msg)
        return True, msg

    # 버그 수정: inferSemanticModel에서 아규먼트를 주입하므로 인자를 가변/선택적으로 처리하도록 시그니처 변경
    def cluster(self, tokenizedDataset=None, datasetID=None):
        """
        this method does the clustering of points based on tokens
        """
        if tokenizedDataset is None:
            tokenizedDataset = self.__dataModel.tokenizedDataset
            
        if self.__dataModel.dataset is None:
            msg = 'Dataset is not initialized, \ndataset must be loaded before start to tokenize'
            self.__logger.error(msg)
            return False, msg
        if tokenizedDataset is None:
            msg = 'before clustering, datapoints must be tokenized'
            self.__logger.error(msg)
            return False, msg
            
        self.__logger.info('creating PointGraph')
        self.pointGraph.createGraph(tokenizedDataset)
        self.pointGraph.printReportOnGraph()

        self.__logger.info('creating similarityGraph')
        self.similarityGraph.findSimilarNodes(ratio=CONFIG.SIMILRATIO)
        self.similarityGraph.refineSimilarityGraph(ratio=CONFIG.REFINERATIO)
        self.__logger.info('creating semanticGraph')
        self.semanticGraph.inferSemanticGraph()

        self.__dataModel.leafNodes = self.pointGraph.leafNodes
        tmp = self.similarityGraph.numberOfConcepts
        self.__dataModel.numberOfClusters = tmp
        tmp = self.similarityGraph.numberOfUniquePoints
        self.__dataModel.numberOfUniquePoints = tmp
        tmp = self.similarityGraph.getUnexplainedLeafNodes(self.__dataModel.leafNodes)
        self.__dataModel.unclusteredPoints = tmp

        self.semanticGraph.getTokenSetOfClasses()
        self.semanticGraph.reportOnBaseClassesUsage()

        self.__dataModel.similarityGraph = self.similarityGraph.graph
        self.__dataModel.semanticGraph = self.semanticGraph.graph

        msg = 'clustering completed'
        self.__logger.info(msg)
        return True, msg

    def __convertListOfPointsInListOfPointTokens(self, dataset):
        pointTokens = {}
        for point in dataset.dataPoints:
            name = point.pointName
            pt = PointTokens(name)
            pointTokens[pt.pointName] = pt
        return pointTokens

    def labelDataset(self, limit, unknown):
        """
        label all points in the dataset according to what is present in the semantic graph
        """
        msg = 'labelling dataset'
        self.__logger.info(msg)
        self.__dataModel.labeledDataset = {}
        for tokenNode in self.pointGraph.leafNodes:
            self.__iterateOverTokensInPoint(tokenNode,
                                            deque(),
                                            tokenNode.pointName,
                                            limit,
                                            unknown)

        msg = 'dataset labelled'
        self.__logger.info(msg)
        return True, msg

    def __iterateOverTokensInPoint(self, tokenNode, tokens, pointName, limit, unknown):
        """get the only predecessor of node and check if it is a concept"""
        # Python 3 대응: NetworkX 2.x 이상 구조의 Iterator 반환 버그 리스트화 처리 방어 조치
        preds = list(self.pointGraph.graph.predecessors(tokenNode))
        if len(preds) > 0:
            parent = preds[0]
        else:
            return
            
        tokens.appendleft(tokenNode.tokenID)
        pointKey = tuple(tokens)
        
        if parent in self.similarityGraph.graph:
            # Python 3 대응: NetworkX 2.x Iterator 호환 가공
            for concept in list(self.similarityGraph.graph.predecessors(parent)):
                if concept in self.semanticGraph.graph:
                    pointLabel = CONSTANTS.UNKNOWNLABEL
                    pointScore = 0.0
                    # Python 3 대응: 명시적 딕셔너리 키 존재 여부 검사 최적화
                    if pointKey in concept.points:
                        pointLabel = concept.points[pointKey][0]
                        pointScore = concept.points[pointKey][1]
                    if pointScore >= limit:
                        self.__labelPoint(pointName, parent.nodeID, pointLabel,
                                          pointScore, concept, unknown)
                                          
        self.__iterateOverTokensInPoint(parent, tokens, pointName, limit, unknown)

    def __labelPoint(self, ptName, instanceID, pointLabel, pointScore, concept, unknown=False):
        labeledDataset = self.__dataModel.labeledDataset

        if unknown and pointLabel == CONSTANTS.UNKNOWNLABEL:
            return

        classLabel = concept.classLabel

        if classLabel != 'nnnn':
            if ptName not in labeledDataset:
                tmp = {}
                tmp['className'] = [classLabel]
                tmp['clusterID'] = [instanceID]
                if classLabel == CONSTANTS.COLLECTIONCLASSLABEL:
                    tmp['label'] = []
                    tmp['distance'] = []
                else:
                    tmp['label'] = [pointLabel]
                    tmp['distance'] = [pointScore]
                labeledDataset[ptName] = tmp
            else:
                if classLabel not in labeledDataset[ptName]['className']:
                    labeledDataset[ptName]['className'].append(classLabel)
                    labeledDataset[ptName]['clusterID'].append(instanceID)
                    if classLabel != CONSTANTS.COLLECTIONCLASSLABEL:
                        labeledDataset[ptName]['label'].append(pointLabel)
                        labeledDataset[ptName]['distance'].append(pointScore)

    def saveLabeledDatasetToFile(self, filename):
        """
        save the labelled to raw file
        """
        labeledDataset = self.__dataModel.labeledDataset
        if labeledDataset is None:
            return False, 'dataset not yet labeled,\nyou need to label the dataset first'
        try:
            # Python 3 대응: with 블록으로 자원 관리 자동화 및 인코딩 가공
            with open(filename, 'w', encoding='utf-8') as outputFile:
                for pointName in sorted(labeledDataset):
                    clusterID = labeledDataset[pointName]['clusterID']
                    className = labeledDataset[pointName]['className']
                    label = labeledDataset[pointName]['label']
                    distance = labeledDataset[pointName]['distance']
                    outputFile.write("%s,\t%s,\t%s,\t%s,\t%s\n" % (pointName, className, clusterID, label, distance))
            return True, 'labeled dataset saved'
        except OSError as error:  # Python 3 대응: IOError -> OSError 및 error.message 버그 제거
            return False, str(error)

    def saveLabeledDataset(self, savePath):
        """
        save the labelled dataset to CSV using pandas
        """
        labeledDataset = self.__dataModel.labeledDataset

        if labeledDataset is None:
            return False, 'dataset not yet labeled,\nyou need to label the dataset first'
        try:
            df = pd.DataFrame(labeledDataset).transpose()
            df.index.name = "pointName"
            df.to_csv(savePath + "AutomapCandidate.csv")
            return df, 'labeled dataset saved'
        except OSError as error:  # Python 3 대응: IOError -> OSError 및 error.message 버그 제거
            return False, str(error)
# -*- coding: utf-8 -*-

import logging

from inference.classifier.device.DeviceClassifier import DeviceClassifier
from inference.classifier.point.PointClassifier import PointClassifier
from inference.classifier.Constants import CONSTANTS
from inference.graphs.Constants import EdgeType


class SemanticInferor:
    """
    this class is responsible for classification of clusters and points.
    """
    def __init__(self, semanticGraph):
        # Python 3 대응: 로거 식별명 최적화
        self.__logger = logging.getLogger(__name__)
        self.__alreadyClassified = []
        self.__semanticGraph = semanticGraph
        self.__deviceClassifier = DeviceClassifier(classifierType=CONSTANTS.DEVICECLASSIFIER)
        self.__pointClassifier = PointClassifier(classifierType=CONSTANTS.POINTCLASSIFIER)

    def classifyClusters(self, tokenSetOfClasses):
        """
        attempts to classify clusters in the semantic graph as equipments.
        It also labels points in each clusters
        """
        if self.__semanticGraph.graph is not None:
            # Python 3 대응: NetworkX 2.x+ 이터레이터 리스트화
            for concept in list(self.__semanticGraph.graph):
                self.__classifyConcept(concept, tokenSetOfClasses)
        self.__alreadyClassified = []  # important to reset the internal state

    def __classifyConcept(self, concept, tokenSetOfClasses):
        """
        attempts to classify a concept/cluster into an equipment

        this method ensures that an equipment cannot contain another one. 
        It also creates a container class
        """
        devClassifier = self.__deviceClassifier
        semanticGraph = self.__semanticGraph.graph
        alreadyClassified = self.__alreadyClassified
        
        if concept.nodeID == '-1906469456':
            pass
            
        classify = True
        setOfLabels = set()  # Python 3 대응: 내장 set 사용
        
        # Python 3 대응: NetworkX 2.x+ 이터레이터 리스트화 적용
        for successor in list(semanticGraph.successors(concept)):
            if semanticGraph[concept][successor][EdgeType.KEY] == EdgeType.ASSOCIATION:
                if successor not in alreadyClassified:
                    alreadyClassified.append(successor)
                    self.__classifyConcept(successor, tokenSetOfClasses)
                newClassLabel = successor.classLabel
                setOfLabels.add(newClassLabel)
                
        if concept.nodeID == '-1906469456':
            pass
        
        if len(setOfLabels) == 1:
            if CONSTANTS.CONTAINERCLASSLABEL in setOfLabels:
                concept.classLabel = CONSTANTS.CONTAINERCLASSLABEL
                alreadyClassified.append(concept)
                classify = False
            if str(CONSTANTS.VAVCLASSLABEL) in setOfLabels:
                concept.classLabel = CONSTANTS.CONTAINERCLASSLABEL
                alreadyClassified.append(concept)
                classify = False
            if str(CONSTANTS.AHUCLASSLABEL) in setOfLabels:
                concept.classLabel = CONSTANTS.CONTAINERCLASSLABEL
                alreadyClassified.append(concept)
                classify = False
            if str(CONSTANTS.VRFCLASSLABEL) in setOfLabels:
                concept.classLabel = CONSTANTS.CONTAINERCLASSLABEL
                alreadyClassified.append(concept)
                classify = False
            elif CONSTANTS.UNKNOWNCLASSLABEL not in setOfLabels:
                concept.classLabel = CONSTANTS.CONTAINERCLASSLABEL
                alreadyClassified.append(concept)
                classify = False
        elif (len(setOfLabels) == 2 and
              ((str(CONSTANTS.AHUCLASSLABEL) in setOfLabels) or (str(CONSTANTS.VRFCLASSLABEL) in setOfLabels))
              and CONSTANTS.UNKNOWNCLASSLABEL in setOfLabels):
            """
            attempt to classify this device: it might be an ahu
            """
            label = devClassifier.classifyDevice(concept, tokenSetOfClasses[concept])
            self.__setDevAndPntLabels(label, concept, tokenSetOfClasses)

            if label == str(CONSTANTS.AHUCLASSLABEL):
                # Python 3 대응: successors 리스트화
                for successor in list(semanticGraph.successors(concept)):
                    if semanticGraph[concept][successor][EdgeType.KEY] == EdgeType.ASSOCIATION:
                        successor.classLabel = CONSTANTS.UNKNOWNCLASSLABEL
            alreadyClassified.append(concept)
            classify = False
        elif (len(setOfLabels) > 1 and
              (str(CONSTANTS.VAVCLASSLABEL) in setOfLabels or
               str(CONSTANTS.AHUCLASSLABEL) in setOfLabels or
               str(CONSTANTS.VRFCLASSLABEL) in setOfLabels)):
            concept.classLabel = CONSTANTS.COMPOSITECLASSLABEL
            alreadyClassified.append(concept)
            classify = False

        if classify and concept in tokenSetOfClasses:
            label = devClassifier.classifyDevice(concept, tokenSetOfClasses[concept])
            self.__setDevAndPntLabels(label, concept, tokenSetOfClasses)
        alreadyClassified.append(concept)

    def __setDevAndPntLabels(self, deviceLabel, concept, tokenSetOfClasses):
        concept.classLabel = deviceLabel
        self.__pointClassifier.labelPointsInConcept(concept, tokenSetOfClasses)

    @property
    def supportedClassLabels(self):
        """returns a list of all the equipment labels as list of strings"""
        return self.__deviceClassifier.supportedClassLabels

    @property
    def supportedPointLabels(self):
        """returns a list of all the equipment labels as list of strings"""
        return self.__pointClassifier.supportedPointLabels
# -*- coding: utf-8 -*-

import sys
import logging


class Classifier:
    """
    Base abstraction layer for point labelling classification task
    """
    def __init__(self):
        # Python 3 대응: 로거 식별명 수정
        self.__logger = logging.getLogger(__name__)

    def labelPointsInConcept(self, concept, setOfTokensOfConcept):
        """
        label points in a concept

        Parameters
        ----------
        concept : ConceptNode
            the node in the semantic graph that needs to be classified
        setOfTokensOfConcept : List
            for every point in deviceClass, a list of tokens
        """
        msg = "This method must be implemented by derived classes"
        self.__logger.error(msg)
        raise NotImplementedError(msg)

    @property
    def supportedPointLabels(self):
        """
        returns a list of supported point labels (strings)
        """
        msg = "This method must be implemented by derived classes"
        self.__logger.error(msg)
        raise NotImplementedError(msg)


class PointClassifier(Classifier):
    """
    this class provides a set of utilities to classify the type of a point
    this class dynamically loads the desired classifier (depending on configuration)
    """
    def __init__(self, classifierType=None):
        self.__logger = logging.getLogger(__name__)
        self.__Package = 'inference.classifier'
        self.__logger.info('loading point classifier component')
        self.__classifier = None
        
        if classifierType is None:
            msg = 'No device classifier has been set, exiting'
            self.__logger.error(msg)
            sys.exit(msg)
            
        try:
            module = __import__(self.__Package + '.' + classifierType,
                                fromlist=['Classifier'])
            classDefinition = getattr(module, 'Classifier')
            self.__classifier = classDefinition()
        except ImportError as error:
            # Python 3 대응: error.message 버그 제거 및 str(error)로 변환 조치
            error_msg = str(error)
            self.__logger.error(error_msg)
            sys.exit(error_msg)

    def labelPointsInConcept(self, deviceClass, setOfTokensOfConcept):
        """
        labels all points of a concept
        """
        return self.__classifier.labelPointsInConcept(deviceClass, setOfTokensOfConcept)

    @property
    def supportedPointLabels(self):
        """
        returns a list of supported point labels (strings)
        """
        return self.__classifier.supportedPointLabels
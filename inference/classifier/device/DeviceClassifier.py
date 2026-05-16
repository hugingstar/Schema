# -*- coding: utf-8 -*-

import sys
import logging


class Classifier:
    """
    Base abstraction layer for device classification task
    """
    def __init__(self):
        # Python 3 대응: 로거 식별 패키지명 동적 매칭화
        self.__logger = logging.getLogger(__name__)

    def classifyDevice(self, concept, setOfTokensOfConcept):
        """
        classifies a concept into device

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
    def supportedClassLabels(self):
        """
        returns a list of supported class labels (strings)
        """
        msg = "This method must be implemented by derived classes"
        self.__logger.error(msg)
        raise NotImplementedError(msg)


class DeviceClassifier(Classifier):
    """
    this class provides a set of utilities to classify the type of a device
    this class dynamically loads the desired classifier (depending on configuration)
    """
    def __init__(self, classifierType=None):
        self.__logger = logging.getLogger(__name__)
        self.__Package = 'inference.classifier.device'
        self.__logger.info('loading device classifier component')
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
            # Python 3 대응: error.message 버그 제거 및 str(error) 변환 조치
            error_msg = str(error)
            self.__logger.error(error_msg)
            sys.exit(error_msg)

    def classifyDevice(self, concept, setOfTokensOfConcept):
        """
        classifies a concept into device
        """
        return self.__classifier.classifyDevice(concept, setOfTokensOfConcept)

    @property
    def supportedClassLabels(self):
        """
        returns a list of supported class labels (strings)
        """
        return self.__classifier.supportedClassLabels
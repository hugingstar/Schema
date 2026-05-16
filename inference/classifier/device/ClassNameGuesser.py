# -*- coding: utf-8 -*-

import sys
import logging


class ClassNameGuesser:
    """
    this class provides a set of utilities to guess the type of an object
    """
    def __init__(self):
        # Python 3 대응: 로거 식별자 최적화
        self.__logger = logging.getLogger(__name__)
        self.__guesserPackage = 'inference.classifier.device.guesser'
        self.__logger.info('loading class guesser component')

    def getClassName(self, typeOfGuesser, node, similarityGraph, pointGraph):
        """
        eventually to be replaced by a dynamic loader
        """
        getter = None
        try:
            module = __import__(self.__guesserPackage + '.' + typeOfGuesser,
                                fromlist=[typeOfGuesser])
            getter = getattr(module, 'guessClassName')
        except ImportError as error:
            # Python 3 대응: error.message 대신 str(error) 사용
            error_msg = str(error)
            self.__logger.error(error_msg)
            sys.exit(error_msg)

        if getter is not None:
            return getter(node, similarityGraph, pointGraph)
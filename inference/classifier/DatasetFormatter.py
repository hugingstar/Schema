# -*- coding: utf-8 -*-

from inference.classifier.Constants import CONSTANTS
from inference.classifier.device.svm_based.Features import FeatureComposer
import sys
import os
import logging
import logging.config


class DatasetFormatter:
    """
    converts a dataset of clusters in formats that are used by machine learning libraries
    """
    def __init__(self):
        # Python 3 대응: 로거 식별 패키지명 동적 매칭 최적화
        self.__logger = logging.getLogger(__name__)
        self.__logger.info('initializing')
        self.__CLUSTERFOLDERS = []
        self.__logger.info('initialized')

    def createLibSVMDataset(self):
        """
        converts a dataset of (labeled) clusters into a libsvm file
        """
        self.__logger.info('creating libsvm dataset')
        print("creating libsvm dataset")  # Python 3 대응: print문 일괄 괄호화
        __testFiles = []

        # 저장할 파일 경로
        __filen = CONSTANTS.LIBSVMDATASETFOLDER + '/' + CONSTANTS.LIBSVMDATASET
        print(__filen)

        # json file upload
        try:
            self.__logger.error(os.getcwd())
            for folder in self.__CLUSTERFOLDERS:
                for jsonFile in os.listdir(folder):
                    if jsonFile.endswith(".json"):
                        self.__logger.info('loading ' + jsonFile)
                        __testFiles.append(folder + '/' + jsonFile)
        except OSError as e:  # Python 3 대응: IOError -> OSError
            self.__logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
            sys.exit()

        tokenIDs = {}
        featureComp = FeatureComposer()
        print(__testFiles)
        for testfile in __testFiles:
            testSet, pointGroundTruth = featureComp.loadTestFile(testfile)
            featureComp.writeLibSVMFileForLabeledPoints(__filen, testSet, pointGroundTruth, tokenIDs)
            
        print("SVM Dataset file Completed!!!")
        self.__logger.info('libsvm dataset created')
        print("Creating Equipment Format File at : " + __filen)

    def addClusterFolder(self, clusterFolder):
        """
        adds a folder containing labeled cluster (written in json)
        """
        self.__CLUSTERFOLDERS.append(clusterFolder)


if __name__ == '__main__':
    logging.config.fileConfig('config/log.conf')
    datasetFormatter = DatasetFormatter()
    datasetFormatter.addClusterFolder(CONSTANTS.TRAININGDATASETFOLDER)
    datasetFormatter.addClusterFolder(CONSTANTS.TESTDATASETFOLDER)
    datasetFormatter.createLibSVMDataset()
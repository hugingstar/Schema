# -*- coding: utf-8 -*-

import joblib  # Python 3 대응: sklearn.externals 내부 경로 삭제에 따른 독립 패키지 전환
import numpy
import logging
from inference.classifier.device.DeviceClassifier import Classifier as CL
from inference.classifier.device.svm_based.Features import FeatureComposer
from inference.classifier.device.svm_based.Models import SVMModels
from inference.classifier.Constants import CONSTANTS
import inference.classifier.device.svm_based.Util as Util


class Classifier(CL):
    """
    SVM-based Device Classifier implementation
    """
    def __init__(self):
        # Python 3 대응: 로거 식별 패키지명 매칭 최적화
        self.__logger = logging.getLogger(__name__)
        
        # load the classifier (Python 3 대응 print문 괄호화)
        print(CONSTANTS.EQUIPMENTSVMMODEL)
        self.__clf = joblib.load(CONSTANTS.EQUIPMENTSVMMODEL)
        
        print(CONSTANTS.EQUIPMENTSCALER)
        self.__scaler = Util.scalerFromJson(CONSTANTS.EQUIPMENTSCALER)
        
        self.__ftComposer = FeatureComposer()
        self.__models = SVMModels()

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
        if len(setOfTokensOfConcept) > 150:
            return CONSTANTS.UNINTELLIGILECLASSLABEL
        if len(setOfTokensOfConcept) < 2:
            return CONSTANTS.UNKNOWNCLASSLABEL
        else:
            setOfTokensOfConcept = self.__ftComposer.preprocessPoints(setOfTokensOfConcept)
            ftrVector = {}
            ftrVectorWithTokens = {}
            self.__logger.error(concept.classLabel)
            self.__ftComposer.getFeatureVector(setOfTokensOfConcept, ftrVector, ftrVectorWithTokens)
            
            inputVector = numpy.zeros((len(ftrVector)))
            for i in range(len(ftrVector)):
                inputVector[i] = ftrVector[i]
                
            # Python 3 대응 및 머신러닝 버그 방어: 최신 sklearn 스케일러/분류기는 2차원 입력을 강제하므로 단일 샘플 포맷으로 변환
            inputVector = inputVector.reshape(1, -1)
            inputVector = self.__scaler.transform(inputVector)
            
            predicted = int(self.__clf.predict(inputVector)[0])
            self.__logger.error('class index: ' + str(predicted))
            return self.__ftComposer.classIndex(predicted)

    @property
    def supportedClassLabels(self):
        """
        returns a list of supported class labels (strings)
        """
        tmp = []
        tmp.append(CONSTANTS.UNKNOWNLABEL)
        tmp.extend(self.__models.EQUIPMENTLABELS)
        return tmp


if __name__ == "__main__":
    test = Classifier()
    print(test.supportedClassLabels)  # Python 3 대응: print문 괄호화
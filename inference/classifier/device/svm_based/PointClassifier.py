# -*- coding: utf-8 -*-

from inference.classifier.device.svm_based.Features import FeatureComposer
from inference.classifier.device.svm_based.Models import SVMModels
from inference.classifier.Constants import CONSTANTS
from inference.classifier.point.PointClassifier import Classifier as CL


class Classifier(CL):
    """ """
    def __init__(self):
        self.__featureComposer = FeatureComposer()
        self.__models = SVMModels()

    def labelPointsInConcept(self, concept, TokenSetOfClasses):
        conceptLabel = concept.classLabel
        ftComp = self.__featureComposer
        if conceptLabel in self.__models.EQUIPMENTPOINT_MODELS:
            model = self.__models.EQUIPMENTPOINT_MODELS[conceptLabel]
        else:
            return None
        points = ftComp.preprocessPoints(TokenSetOfClasses[concept])
        tmpMx = {}
        for key in model:
            tmpMx[key] = []
            for n, point in enumerate(points):
                tmpMx[key].append(ftComp.getHighestMatchingScore(point, model[key]))

        numOfLabels = len(list(model.keys()))
        numOfPts = len(points)
        for i in range(numOfLabels):
            maxLabelKey, maxPoint, maxScore = self.__findMaxInMatrix(tmpMx, numOfPts)
            pointKey = tuple(TokenSetOfClasses[concept][maxPoint])
            concept.labelPoint(pointKey, maxLabelKey, maxScore)
            del tmpMx[maxLabelKey]
            for key in tmpMx:
                tmpMx[key][maxPoint] = -1

    def __findMaxInMatrix(self, matrixScore, numOfPts):
        ptSort = {}
        maxPts = []
        for key in matrixScore:
            tmp = matrixScore[key]
            tmp1 = sorted(range(numOfPts), key=lambda x: tmp[x], reverse=True)
            maxPts.append(tmp[tmp1[0]])
            ptSort[key] = tmp1

        numOfLbs = len(list(matrixScore.keys()))
        tmpLabel = sorted(range(numOfLbs), key=lambda x: maxPts[x], reverse=True)

        # Python 3 대응: dict_keys 뷰 객체의 다이렉트 인덱싱 제한 우회를 위해 명시적 list() 래핑 가공
        maxLabel = list(matrixScore.keys())[tmpLabel[0]]
        maxValue = maxPts[tmpLabel[0]]
        maxPoint = ptSort[maxLabel][0]
        return maxLabel, maxPoint, maxValue 

    @property
    def supportedPointLabels(self):
        """
        returns a list of supported point labels (strings)
        """
        tmp = []
        tmp.append(CONSTANTS.UNKNOWNLABEL)
        tmp.extend(self.__models.POINTLABELS)
        return tmp
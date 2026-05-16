# -*- coding: utf-8 -*-

import jellyfish as jf
import logging
import json
import os
from inference.classifier.device.svm_based.Models import SVMModels
from inference.classifier.Constants import CONSTANTS
from inference.classifier.RulesConstants import KEYS
from inference.graphs.nodes.PointNode import ConceptNode
import inference.classifier.device.svm_based.Util as Util


class FeatureComposer:
    """
    this class provides the capabilities to compute features from clusters and equipment models.
    Features can be used later for learning/ classification purposes
    """
    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__cache = {}
        self.__models = SVMModels()

    def loadTestFile(self, testFile):
        """
        load a JSON test file containing also the groundtruth
        """
        testSet = {}
        pointGroundTruth = {}
        try:
            # Python 3 대응: 오픈 시 인코딩 명시
            with open(testFile, 'r', encoding='utf-8') as jsonTestFile:
                testdata = json.load(jsonTestFile)
                index = 0
                print("!!", jsonTestFile)  # Python 3 대응: print문 괄호화

                for classData in testdata[KEYS.CLASSES]:
                    classLabel = str(classData[KEYS.LABEL])
                    concept = ConceptNode([str(index)], '')
                    concept.classLabel = classLabel
                    index += 1

                    testSet[concept] = []
                    pointGroundTruth[concept] = {}
                    for point in classData[KEYS.POINTS]:
                        key = Util.getKeyFromPoint(point[KEYS.POINT])
                        pointGroundTruth[concept][key] = str(point[KEYS.LABEL])
                        tmp = []
                        for token in point[KEYS.POINT]:
                            tmp.append(str(token))
                        testSet[concept].append(tmp)
                return testSet, pointGroundTruth
        except OSError as e:  # Python 3 대응: IOError -> OSError
            print("Warning: I/O error({0}): {1}".format(e.errno, e.strerror))
            return {}, {}

    def getFeatureVector(self, pointsInCluster, featureVector=None, featureVectorWithTokens=None):
        """
        returns the feature vector corresponding to the model and the cluster
        provided as inputs
        """
        # Python 3 대응: 지원 중단된 iteritems() 대신 items() 메서드 적용
        for eqLabel, model in self.__models.EQUIPMENT_MODELS.items():
            print("[EQ_LABEL] :", eqLabel)
            if featureVector is None:
                featureVector = {}
                featureVectorWithTokens = {}
            featureCounter = len(featureVector)
            featureVectorWithTokens[featureCounter] = 0
            total = 0
            prod = 1

            for modelPoint in model:
                tmp = 0
                i = 0
                maxScore = 0
                maxIndex = 0
                tmtm = []
                if 1 < len(pointsInCluster) < 150:
                    for point in pointsInCluster:
                        tmp = self.getHighestMatchingScore(point, model[modelPoint])
                        tmtm.append(tmp)
                        if maxScore < tmp:
                            maxScore = tmp
                            maxIndex = i
                        i += 1
                    total += maxScore
                    prod = prod * maxScore
            tmp = total / float(len(model))
            featureVector[featureCounter] = pow(3 * tmp, 2)
            featureVectorWithTokens[featureCounter] = [modelPoint, pointsInCluster[maxIndex]]
            print("[maxIndex] :", maxIndex, "[modelPoint] :", modelPoint, "[Point] :", pointsInCluster[maxIndex])
            print("[Feature length] :", featureCounter, "[Model len] :", len(model), "[Score average] :", tmp, "fv : ", pow(tmp * 3, 2))

            print(featureVector)
            print(featureVectorWithTokens)

            featureCounter += 1
        return featureVector, featureVectorWithTokens

    def getHighestMatchingScore(self, point, modelPoint):
        """
        가장 높은 매칭 스코어를 획득
        """
        score = 0
        for modelAlternative in modelPoint:
            tmp = self.__getScore(point, modelAlternative)
            if score < tmp:
                score = tmp
        return score

    def __getScore(self, tokens, otherTokens):
        lenTokens = len(tokens)
        lenOtherTokens = len(otherTokens)
        if lenTokens == 0 or lenOtherTokens == 0:
            return 0.0
        if tokens == otherTokens:
            return 1.0

        coeff = max(lenTokens, lenOtherTokens)
        scores = 0
        for token in tokens:
            token = str(token)  # Python 3 대응: unicode() 형변환 제거 및 str() 대체
            tmpScore = 0
            for otherToken in otherTokens:
                otherToken = str(otherToken)  # Python 3 대응: unicode() -> str()
                tmp = self.__computeTokenDistance(token, otherToken)
                if tmp > 0.85 and tmp > tmpScore:
                    tmpScore = tmp
            scores += tmpScore
        scores = scores / float(coeff)

        newToken = str("".join(tokens))  # Python 3 대응: unicode() -> str()
        if len(otherTokens) == 1:
            weight = 1
            len1 = len(newToken)
            len2 = len(otherTokens[0])

            if len1 > len2:
                weight = len2 / float(len1)
            elif len2 > len1:
                weight = len1 / float(len2)

            tmp = self.__computeTokenDistance(newToken, otherTokens[0])
            if tmp * weight > scores and tmp * weight > 0.1:
                scores = tmp * weight
        return scores

    def __computeTokenDistance(self, token, otherToken):
        """
        토큰 사이의 길이를 계산
        """
        key = (token, otherToken)
        tmp = 0

        if key in self.__cache:
            tmp = self.__cache[key]
        else:
            # Python 3 대응: 불필요한 유니코드 변환부 일원화 정리
            tmp = jf.jaro_winkler(token, str(otherToken))
            self.__cache[key] = tmp
        return tmp

    def writeLibSVMFileForLabeledPoints(self, filename, testSet, pointGroundTruth, tokenHashMap):
        """
        creates a libSVM sample file using a model for all points in equipment that are prelabelled.
        """
        if tokenHashMap is None:
            print('new token set')
            tokenHashMap = {}

        # preprocess tokens
        for concept in testSet:
            testSet[concept] = self.preprocessPoints(testSet[concept])

        # Python 3 대응: 자원 누수 누적 방지 및 인코딩 처리를 위해 with open 구문 동시 선언 결합
        with open(filename, 'a', encoding='utf-8') as outputFile, \
                open(filename + '_model.debug', 'a', encoding='utf-8') as outputDebugFile:

            for concept in testSet:
                sample = ''
                sampleDeb = ''

                deviceType = str(self.__classCodes(concept.classLabel))

                print("Concept : ", concept)
                print("Concept label :", concept.classLabel)
                print("DeviceType :", deviceType)

                if not deviceType == '-1':
                    sample = deviceType + '\t'
                    sampleDeb = sample
                    featureCounter = 0
                    featureVtr = {}
                    featureVtrWithTk = {}

                    self.getFeatureVector(testSet[concept], featureVtr, featureVtrWithTk)

                    featureCounter += len(featureVtr)
                    for feature in range(len(featureVtr)):
                        sample += str(feature) + ':' + str(featureVtr[feature]) + '\t'
                        if feature in featureVtrWithTk:
                            sampleDeb += '(' + str(featureVtrWithTk[feature][0])
                            sampleDeb += ',' + str(featureVtrWithTk[feature][1])
                            sampleDeb += ') ' + str(feature) + ':'
                            sampleDeb += str(featureVtr[feature]) + '\t'
                    sample += '\n'
                    sampleDeb += '\n'
                    outputFile.write(sample)
                    outputDebugFile.write(sampleDeb)
                print(" ")

    def preprocessPoints(self, points):
        """
        불필요한 토큰을 제거한다.
        """
        newPoints = []
        for point in points:
            newPoints.append(self.preprocessTokens(point))
        newPoints = self.removeCommonToken(newPoints)

        out = 'preprocessed points\n'
        for point in newPoints:
            out += str(point) + '\n'

        self.__logger.debug(out)
        return newPoints

    def removeCommonToken(self, points):
        """
        recursively remove common tokens from points
        """
        if len(points) > 1:
            tmpPoints = [points[0][1:]]
            for n in range(len(points) - 1):
                if len(points[n]) > 0 and len(points[n + 1]) > 0:
                    if points[n][0] == points[n + 1][0]:
                        tmpPoints.append(points[n + 1][1:])
                    else:
                        return points
                else:
                    return points
            points = self.removeCommonToken(tmpPoints)
        return points

    def preprocessTokens(self, tokens):
        """
        preprocess removes all numbers because they are redundant
        """
        tmp = []
        for token in tokens:
            if not token.isdigit():
                tmp.append(token)
        return tmp

    def classIndex(self, index):
        # Python 3 대응: dict_keys 구조를 list()화 하여 슬라이싱 및 역매핑 안전화
        keys = list(self.__models.EQUIPMENT_MODELS.keys())
        if len(keys) < index or index == 0:
            return CONSTANTS.UNKNOWNLABEL
        else:
            return keys[index - 1]

    def __classCodes(self, label):
        # Python 3 대응: 인덱스 조회를 위해 명시적 list() 화 진행
        keys = list(self.__models.EQUIPMENT_MODELS.keys())
        if label in keys:
            return keys.index(label) + 1
        else:
            return 0

    def c(self, filename):
        extensions = ['.libsvm', '.debug']
        for root, dirs, files in os.walk('.'):
            for currentFile in files:
                try:
                    if any(currentFile.endswith(ext) for ext in extensions):
                        print('removing ', os.path.join(root, currentFile))
                        with open(os.path.join(root, currentFile), 'w', encoding='utf-8') as outputFile:
                            outputFile.write('')
                except Exception:  # Python 3 대응: naked except 정돈
                    pass
# -*- coding: utf-8 -*-

import logging
from inference.classifier.Constants import CONSTANTS


class NODETYPE:
    """
    an enumeration of possibly point types
    """
    BASE = 0
    POINT = 1
    OBJECT = 2
    QUALIFIER = 3


class TokenNode:
    """
    objects of this class represents a token in the token graph
    """
    def __init__(self, nodeID, tknID, pointName=None, nodeType=NODETYPE.BASE):
        self.nodeID = nodeID
        self.tokenID = tknID
        self.nodeType = nodeType
        self.numberOfMembers = None
        self.pointName = pointName
        self.usable = True

    @property
    def usable(self):
        return self.__usable

    @usable.setter
    def usable(self, isUsable):
        self.__usable = isUsable

    @property
    def nodeID(self):
        return self.__nodeID

    @nodeID.setter
    def nodeID(self, nodeID):
        self.__nodeID = nodeID

    @property
    def tokenID(self):
        return self.__tokenID

    @tokenID.setter
    def tokenID(self, tokenID):
        self.__tokenID = tokenID

    @property
    def nodeType(self):
        return self.__nodeType

    @property
    def pointName(self):
        return self.__pointName

    @pointName.setter
    def pointName(self, pointName):
        if pointName is not None:
            self.__pointName = pointName

    @nodeType.setter
    def nodeType(self, nodeType):
        if nodeType == NODETYPE.BASE:
            self.__nodeType = NODETYPE.BASE
        elif nodeType == NODETYPE.OBJECT:
            self.__nodeType = NODETYPE.OBJECT
        elif nodeType == NODETYPE.POINT:
            self.__nodeType = NODETYPE.POINT
        elif nodeType == NODETYPE.QUALIFIER:
            self.__nodeType = NODETYPE.QUALIFIER

    def __repr__(self):
        out = '[nodeID:' + str(self.nodeID) + ', tokenID:' + \
            str(self.tokenID) + ', nodeType:' + str(self.nodeType) + ']'
        return out

    def __ne__(self, other):
        if isinstance(other, TokenNode):
            return not self.__eq__(other)
        else:
            return True

    def __eq__(self, other):
        if isinstance(other, TokenNode):
            return self.nodeID == other.nodeID
        else:
            return False

    def __hash__(self):
        return hash(self.nodeID)

    def getHashCode(self):
        return self.__hash__()


class ConceptNode:
    """
    a class to represent concepts in the semantic model
    """
    def __init__(self, members, nodeName=''):
        self.__logger = logging.getLogger(__name__)
        self.members = members  # the list of child tokens
        self.__nodeID = None
        self.nodeName = nodeName
        self.classLabel = CONSTANTS.UNKNOWNLABEL
        self.__points = {}  # the list of points
        self.instancesID = []

    @property
    def classLabel(self):
        return self.__classLabel

    @classLabel.setter
    def classLabel(self, label):
        self.__classLabel = label

    @property
    def nodeName(self):
        return str(self.__nodeName)

    @nodeName.setter
    def nodeName(self, nodeName):
        self.__nodeName = nodeName

    @property
    def nodeID(self):
        if self.members is not None:
            self.__nodeID = hash(self)
        return str(self.__nodeID)

    def addMember(self, member):
        if member not in self.members:
            self.members.append(member)

    def addMembers(self, members):
        for member in members:
            self.addMember(member)

    def removeMember(self, member):
        if member in self.members:
            self.members.remove(member)

    @property
    def members(self):
        return self.__members

    @members.setter
    def members(self, members):
        self.__members = members

    def hasMember(self, member):
        if member in self.members:
            return True
        return False

    @property
    def points(self):
        return self.__points

    def addPoint(self, tokenNodes, label, distance):
        key = []
        if len(tokenNodes) > 0:
            for tokenNode in tokenNodes:
                key.append(tokenNode.tokenID)
            key = tuple(key)
            self.points[key] = [label, distance, tokenNodes[0].pointName]
                    
        
    def labelPoint(self, key, label, distance):
        if key in self.points:
            self.points[key][0] = label
            self.points[key][1] = distance

    @property
    def numberOfInstances(self):
        return self.__numberOfInstances

    @numberOfInstances.setter
    def numberOfInstances(self, numb):
        self.__numberOfInstances = numb

    @property
    def instances(self):
        return self.__instancesID

    @instances.setter
    def instances(self, instances):
        self.__instancesID = instances

    def isDerivedFrom(self, other):
        """
        determines if the current node is derived from other:
        it means that a this node has all members other plus at least an
        additional one
        """
        if len(other.members) > 2:
            if len(self.members) > len(other.members):
                for member in other.members:
                    if member not in self.members:
                        return False
                return True
        return False

    def isSameAs(self, other):
        """
        determines if the current node is the same as other
        """
        if isinstance(other, ConceptNode):
            # 버그 수정: 오타가 보였던 다른 객체의 매직 메서드 직접 호출부를 표준 내장 hash 함수로 대체하여 안전성 확보
            return hash(self) == hash(other)
        return False

    def isGeneralizationOf(self, other, ratio):
        """
        determines if the current node is a generalization of other
        """
        counter = 0
        if len(self.members) > 2:
            if len(self.members) < len(other.members):
                # 버그 수정: 존재하지 않던 getMembers() 호출부 오류를 프로퍼티인 self.members로 수정
                for member in self.members:
                    if member not in other.members:
                        return False
                    else:
                        counter += 1
                if counter >= float(len(other.members)) * ratio:
                    return True
        return False

    def findCommonMembers(self, other, ratio):
        """
        returns the common members between the two nodes if the number of this
        member is larger than ratio times of the numbers of member of each node
        """
        commonNodes = []
        ms1 = []
        ms2 = []
        if len(self.members) >= len(other.members):
            ms1 = self.members
            ms2 = other.members
        else:
            ms2 = self.members
            ms1 = other.members

        for member in ms2:
            if member in ms1:
                commonNodes.append(member)

        if (len(commonNodes) >= float(len(ms2)) * ratio) and \
                (len(commonNodes) >= float(len(ms1)) * ratio):
            return commonNodes
        return []

    def __repr__(self):
        out = '[nodeID:' + str(self.nodeID) + ', nodeName:' + str(self.nodeName) + ']'
        return out

    def __ne__(self, other):
        if isinstance(other, ConceptNode):
            return not self.__eq__(other)
        else:
            return True

    def __eq__(self, other):
        if isinstance(other, ConceptNode):
            return self.nodeID == other.nodeID
        else:
            return False

    def __hash__(self):
        if self.__nodeID is None:
            self.__nodeID = hash(frozenset(self.members))
        return self.__nodeID
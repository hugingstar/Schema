# -*- coding: utf-8 -*-
import logging


class Token:
    """
    this class provides utilities and data structures for a token
    """
    def __init__(self, token_name):
        self.__logger = logging.getLogger(__name__)
        if token_name != '' and token_name is not None:
            self.__name = token_name
            self.__children = [] 
            """references to the new tokens when a token is split"""
            self.__parents = []  # reference to parents tokens if this token results from a split
            self.__descendants = None  # list of references to all 'descendants' of a Token
            self.__frequency = 1
            self.__pointName = None  # Python 3 대응: 초기화 누락 방어
            self.simple_frequency = 1  
            self.size = len(token_name)
        else:
            raise NameError('the name of a token cannot be an empty string. Supplied token_name="' + str(token_name) + '"')

    def hasChildren(self):
        if len(self.__children) > 0:
            return True
        else:
            return False  # 버그 수정: return 키워드 추가

    def hasParents(self):
        if len(self.__parents) > 0:
            return True
        else:
            return False  # 버그 수정: return 키워드 추가
            
    @property
    def pointName(self):
        return self.__pointName

    @pointName.setter
    def pointName(self, pointName):
        self.__pointName = pointName
        
    @property        
    def name(self):
        return self.__name        
        
    def addChild(self, child):
        if child != self:
            if child not in self.__children:
                self.__children.append(child)
                child.addParent(self)
                child.increaseFrequency(self.__frequency - 1)
            
    def addParent(self, parent):        
        if parent != self:
            if parent not in self.__parents:
                self.__parents.append(parent)
                
    @property    
    def children(self):
        return self.__children
    
    @property
    def parents(self):
        return self.__parents

    def __resolveChildList(self, childList):
        """
        find all the tokens that are "descendant" of the current one. It must preserve the order of tokens
        """
        if len(self.__children) == 0:  
            childList.append(self)
        else:
            for token in self.__children:            
                token.__resolveChildList(childList)
                
        return childList

    @property                                
    def descendants(self):
        """
        returns the "descendants of a token"
        """
        if self.__descendants is None or len(self.__descendants) == 0:
            self.__descendants = []
            self.__descendants = self.__resolveChildList(self.__descendants)             
        return self.__descendants
        
    @descendants.setter                                
    def descendants(self, descendants):
        self.__descendants = descendants
    
    @property
    def frequency(self):
        return self.__frequency    
    
    @frequency.setter
    def frequency(self, frequency):
        self.__frequency = frequency
    
    def increaseFrequency(self, delta_frequency):
        self.__frequency += delta_frequency
        
    def printToken(self):
        form = self.formatToken()
        tmp = 'name: ' + form[0] + ', children: ' + form[1] + ', '
        tmp += 'parents: ' + form[2] + ', frequency: ' + form[3]
        return tmp
    
    def formatToken(self):
        children = ''
        for child in self.__children:
            children += child.name + ', '
        parents = ''
        for par in self.__parents:
            parents += par.name + ', '

        return [self.__name, '[' + children + ']', '[' + parents + ']', str(self.frequency)] 

    def __repr__(self):      
        return self.printToken()    
        
    def __ne__(self, other):
        if isinstance(other, Token):
            return not self.__eq__(other)
        else:
            return True
    
    def __eq__(self, other):
        if isinstance(other, Token):
            return self.__name == other.__name
        return False
    
    # Python 3 대응: 지원 중단된 __cmp__ 대신 __lt__ 구현 분기 조치
    def __lt__(self, other):
        if isinstance(other, Token):
            return self.frequency < other.frequency
        return NotImplemented
            
    def __hash__(self):
        return hash(self.__name)
      

class PointTokens:
    """
     this class provides utilities on the tokens for a point 
    """
    def __init__(self, pointName):
        self.__tokens = []
        self.__uniqueTokens = None
        self.__pointName = pointName
        self.__pointDefinition = {}  # 버그 수정: 게터와 명칭 일치 처리
    
    @property
    def tokens(self):
        return self.__tokens
        
    @tokens.setter
    def tokens(self, tokens):
        self.__tokens = tokens
        self.__uniqueTokens = None  # 토큰 업데이트 시 고유 토큰 캐시 초기화 보장
    
    @property
    def uniqueTokens(self):
        if self.__uniqueTokens is None:            
            self.__uniqueTokens = set(self.tokens)
        return self.__uniqueTokens
    
    @property    
    def pointName(self):
        return self.__pointName
    
    @property    
    def pointDefinition(self):
        return self.__pointDefinition
    
    @pointDefinition.setter    
    def pointDefinition(self, pointDefinition):
        self.__pointDefinition = pointDefinition        

    def __eq__(self, other):
        if isinstance(other, PointTokens):
            return self.tokens == other.tokens and self.pointName == other.pointName   
        return False
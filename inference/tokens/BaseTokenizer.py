# -*- coding: utf-8 -*-

import re

from inference.tokens.PointTokens import PointTokens
from inference.tokens.PointTokens import Token


class BaseTokenizer:
    """
    base tokenizer class: every variation of tokenization algorithm must
    derive from this class
    """
    def __init__(self):
        self.__tokenized_containter = {}
        self.__simple_frequencies = {}
        self.__unique_frequencies = {}
        self.__tokenSet = {}

    def tokenize(self, pointToken):
        """
        tokenize a PointTokens
        @return a PointTokens
        """
        raise NotImplementedError('This method must be implemented in derived classes')

    def tokenizePointList(self, pointList):
        """
        tokenize a list of PointTokens.
        @return a dictionary: keys are point names and values are PointTokens
        """
        self.__tokenSet = {}
        self.__tokenized_containter = {}
        for pointName in pointList:
            pnToken = PointTokens(pointName)
            self.__tokenized_containter[pointName] = self.tokenize(pnToken)

        return self.__tokenized_containter

    # 버그 수정: 외부 인자를 전달받는 잘못된 @property 데코레이터 일괄 제거 및 일반 메서드로 변환
    def frequecyOfTokens(self, tokenized_containter=None):
        return self.sortTokenSetByFrequency()

    def listOfTokens(self, tokenized_containter):
        tmp = []
        for point_name in tokenized_containter:
            tmp.extend(tokenized_containter[point_name].tokens)
        return tmp

    def listOfUniqueTokens(self, tokenized_containter):
        tmp = []
        for point_name in tokenized_containter:
            tmp.extend(tokenized_containter[point_name].uniqueTokens)
        return tmp

    @property
    def tokenSet(self):
        return self.__tokenSet

    @tokenSet.setter
    def tokenSet(self, tokenSet):
        self.__tokenSet = tokenSet

    def splitTrailingQualifiers(self, token):
        """
        splits the trailing digit(s) and consider them as new token(s)
        """
        regularexp = '.*?([0-9]+)$'

        tmp = re.match(regularexp, token)
        primary_token = ''
        digits = ''
        if tmp is not None:
            digits = tmp.group(1)
            li = token.rsplit(digits, 1)
            primary_token = primary_token.join(li)
        else:
            primary_token = token

        out = []
        if primary_token == '':
            out = [digits]
        elif digits == '':
            out = [primary_token]
        else:
            out = [primary_token, digits]

        return out

    def splitOnNumber(self, token):
        """
        split token containing a number in between
        """
        return re.findall(r"[^\W\d_]+|\d+", token)

    def normalizeTokens(self):
        """
        for each token that has more than 2 (non-numeric) characters, find all
        the tokens containing that token.
        for each match, split the match and generate a new token
        """
        tmp = {}
        for token_name in self.tokenSet:
            tk = self.splitTrailingQualifiers(token_name)
            tmp[token_name] = []
            for t1 in tk:
                tmp[token_name].append(t1)

        for token_name in tmp:
            self.__addChildTokensToSet(tmp[token_name], token_name)

        for token_name in self.tokenSet:
            tk = self.splitOnNumber(token_name)
            tmp[token_name] = tk

        for token_name in tmp:
            self.__addChildTokensToSet(tmp[token_name], token_name)

        for n in [1, 2]:
            already_matched = []
            # sort by length of token in ascending order
            tmp_sorted = self.sortTokenSetByTokenLenght()
            total_len = len(tmp_sorted)
            for i in range(total_len):
                token_name = tmp_sorted[i].name
                if len(token_name) >= 3 and not (i in already_matched):
                    for k in range(i + 1, total_len, 1):
                        if not (k in already_matched):
                            oTkName = tmp_sorted[k].name
                            splitted = oTkName.split(token_name)
                            if len(splitted) == 2:
                                for tk in splitted:
                                    parts = re.match('^([0-9]+)([A-Z]+)', tk)
                                    if parts is not None:
                                        already_matched.append(k)
                                        parts = parts.groups()
                                        self.__addChildTokensToSet(parts, oTkName)
                                    else:
                                        parts = re.match('^([0-9]+)', tk)
                                        if parts is not None:
                                            already_matched.append(k)
                                            name = parts.group()
                                            self.__addChildTokensToSet([name], oTkName)

        # split all trailing digits from tokens
        for token in self.sortTokenSetByTokenLenght():
            tk = self.splitTrailingQualifiers(token.name)
            self.__addChildTokensToSet(tk, token.name)
        return self.sortTokenSetByFrequency()

    def __addChildTokensToSet(self, parts, originalTokenName=None):
        for part in parts:
            self.addTokenToSet(part, originalTokenName)

    def addTokenToSet(self, token_or_token_name, originalTokenName=None):
        """
        add a token to the dictionary of tokens. If the token exists then it
        just increases its frequency input argument can be either a string
        (name of the token) or a token instance
        """
        try:
            if isinstance(token_or_token_name, Token):
                token_name = token_or_token_name.name
                token = token_or_token_name
            elif isinstance(token_or_token_name, str):  # Python 3 대응: basestring -> str 변경
                token_name = token_or_token_name
                token = None
            else:
                raise TypeError('argument must be either a string or a Token')

            if token_name not in self.__tokenSet:
                token = Token(token_name)
                self.__tokenSet[token_name] = token
            else:
                token = self.__tokenSet[token_name]
                token.increaseFrequency(1)
            if originalTokenName is not None:
                self.__tokenSet[originalTokenName].addChild(token)
                
            return token
        except NameError as error:
            print(error)  # Python 3 대응: print문 괄호화
            return None

    def sortTokenSetByFrequency(self, tkSet=None):
        if tkSet is None:
            tkSet = self.__tokenSet
        tmp = sorted(tkSet.items(), key=lambda x: x[1].frequency, reverse=True)
        tmp = [y for x, y in tmp]
        return tmp

    def sortTokenSetByTokenLenght(self, tkSet=None, reverse=False):
        if tkSet is None:
            tkSet = self.__tokenSet
        tmp = sorted(tkSet.items(), key=lambda x: x[1].size, reverse=reverse)
        tmp = [y for x, y in tmp]
        return tmp
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 16:28:10 2015

@author: leonarf
"""
from inference.tokens.BaseTokenizer import BaseTokenizer


class SimpleTokenizer(BaseTokenizer):
    """
    @brief this class tokenize a point name
    """
    def __init__(self):
        super().__init__()  # Python 3 대응: super() 구문 간소화
        self.first_separator = '/'

    def tokenize(self, pointToken):
        tokens = []
        output = []
        point_name = pointToken.pointName
        point_name = self.__unCamel(point_name)
        point_name = point_name.upper()
        point_name = point_name.replace('#', '')
        point_name = point_name.replace('-', ' ')
        point_name = point_name.replace('_', ' ')
        point_name = point_name.replace('.', ' ')
        point_name = point_name.replace(':', ' ')
        partial_tokens = point_name.split(self.first_separator)
        for ptoken in partial_tokens:
            tokens.extend(ptoken.split(' '))
            
        # remove all empty tokens
        for token_name in tokens:
            if token_name != '':
                token_name = token_name.strip()
                token = self.addTokenToSet(token_name)
                output.append(token)

        pointToken.tokens = output
        return pointToken

    def __unCamel(self, inputString):
        """
        this method "un-camelizes" a camel string
        """
        if not inputString:
            return ""
            
        # Python 3 대응 및 방어 조치: 문자열 길이가 극도로 짧은 경우 예외 처리 안전망 강화
        if len(inputString) < 3:
            return "".join([c.upper() for c in inputString])

        output = [inputString[0].upper()]
        c1 = ''
        c2 = ''
        divide = False
        
        for i in range(1, len(inputString) - 2, 1):
            c = inputString[i]
            c1 = inputString[i + 1]
            c2 = inputString[i + 2]
            output.append(c.upper())
            if divide:
                output.append(' ')
                divide = False
            if c.islower() and c1.isupper():
                output.append(' ')
            elif c.isupper() and c1.isupper() and c2.islower():
                divide = True
                
        output.append(c1.upper())
        if divide:
            output.append(' ')
        output.append(c2.upper())
        
        return "".join(output)  # Python 3 대응: str.join('', output)을 ''.join(output)으로 교체
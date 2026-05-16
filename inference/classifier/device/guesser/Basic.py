# -*- coding: utf-8 -*-

"""
    guess the class name of the current node
"""


def guessClassName(nodeType, similarityGraph, pointGraph):
    first_name = ''        
    second_name = ''
    
    # Python 3 대응: NetworkX 2.x 이상 이터레이터 뷰 반환 구조의 list 변환 조치
    successors_nodes = list(similarityGraph.successors(nodeType))
    if len(successors_nodes) == 0:
        return nodeType.nodeID
    else:        
        node = successors_nodes[0]
        last_name = node.tokenID
        
        preds = list(pointGraph.predecessors(node))        
        if len(preds) > 0:                
            first_name = preds[0].tokenID
            
        succs = list(pointGraph.successors(node))
        if len(succs) > 0:                
            second_name = succs[0].tokenID
    
        if first_name.isdigit():
            first_name = ''
        if second_name.isdigit():
            second_name = ''
        if last_name.isdigit():
            last_name = ''
            
        return first_name + '_' + second_name + '_' + last_name
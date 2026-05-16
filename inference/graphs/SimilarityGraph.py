# -*- coding: utf-8 -*-

import networkx as nx
import logging

from inference.graphs.nodes.PointNode import ConceptNode
from inference.classifier.device.ClassNameGuesser import ClassNameGuesser
from inference.graphs.Constants import NODE


class SimilarityGraph:
    """
    this class encapsulates a collection of utilities for the creation of a
    graph out of point names and operations on it
    """
    def __init__(self, pointGraph, classGuesserType='Basic'):
        self.__logger = logging.getLogger(__name__)
        self.__logger.info('initialization')
        self.__classGuesser = ClassNameGuesser()
        self.__classGuesserType = classGuesserType
        self.__ptGU = pointGraph
        self.__unexplainedLeafNodes = None
        self.graph = None

    @property
    def graph(self):
        return self.__graph

    @graph.setter
    def graph(self, graph):
        self.__graph = graph

    def findSimilarNodes(self, ratio=0.9):
        """
        find similar nodes in the graph. Similarity is defined as having as the
        number of successors of the same type
        """
        self.__logger.info('starting comparing nodes')
        self.__logger.info('nodes are considered similar when they have' + str(ratio) + ' edges with the same label')

        self.__unexplainedLeafNodes = None
        similarityGraph = nx.DiGraph()
        self.graph = similarityGraph
        pointGraph = self.__ptGU.graph
        nodes = list(pointGraph.nodes())  # Python 3 대응: NodeView 리스트화
        number_of_nodes = len(pointGraph)
        n = 0
        for node in nodes:
            if node not in similarityGraph and node.usable:
                n += 1
                self.__logger.info('considering node' + str(n) + ' out of' + str(number_of_nodes) + ' nodes')
                for succ_node in list(pointGraph.successors(node)):
                    pssNodes = self.__ptGU.findParentsOfSimilarTypes(succ_node)
                    for otNode in pssNodes:
                        if otNode.usable and (node != otNode):
                            similarNodes = self.__getSimilarNodes(node)
                            if otNode not in similarNodes:
                                if self.__areNodesSimilar(node, otNode, ratio):
                                    self.__addSimilarNode(node, otNode)

        # attempts to assign a name to each concept
        for concept in list(similarityGraph.successors(NODE.CONCEPT)):
            tmp = self.__classGuesser.getClassName(self.__classGuesserType,
                                                   concept,
                                                   similarityGraph,
                                                   pointGraph)
            concept.nodeName = tmp

    def refineSimilarityGraph(self, ratio=0.9):
        """
        refines the similarityGraph by clustering similar nodes within each
        concept
        """
        similarityGraph = self.graph
        refinement = {}
        self.__logger.info('refining similarityGraph...')
        for concept in list(similarityGraph.successors(NODE.CONCEPT)):
            already_visited = []
            successors_nodes = list(similarityGraph.successors(concept))
            for node in successors_nodes:
                if node not in already_visited:
                    already_visited.append(node)
                    for otherNode in successors_nodes:
                        if (otherNode not in already_visited) and (node != otherNode):
                            if self.__areNodesSimilar(node, otherNode, ratio):
                                newConcept = ConceptNode(self.__ptGU.getMembersOfNodeInPointGraph(node))
                                if newConcept not in refinement:
                                    refinement[newConcept] = set()  # Python 3 대응: 내장 set 사용

                                refinement[newConcept].add(node)
                                refinement[newConcept].add(otherNode)
                                already_visited.append(otherNode)

        for concept in refinement:
            if len(refinement[concept]) > 0 and concept not in similarityGraph:
                for node in refinement[concept]:
                    self.__refineSimilarNode(concept, node)

                tmp = self.__classGuesser.getClassName(self.__classGuesserType,
                                                       concept,
                                                       similarityGraph,
                                                       self.__ptGU.graph)
                concept.nodeName = tmp
                self.__logger.info('added concept, ' + str(concept))
            else:
                self.__logger.warning('????, ' + str(concept))
            self.__logger.info('done refining similarityGraph')

        self.__cleanUpSimilarityGraph(ratio)

    def __cleanUpSimilarityGraph(self, ratio=0.9):
        """
        remove children of concepts that belongs to a very similar concept
        """
        similarityGraph = self.graph
        for concept in list(similarityGraph.successors(NODE.CONCEPT)):
            for node in list(similarityGraph.successors(concept)):
                self.__cleanupDescendants(node, concept)

    def __cleanupDescendants(self, anchestorNode, anchestorConcept, currentNode=None, ratio=0.8, alreadyVisited=None):
        pointGraph = self.__ptGU.graph
        similarityGraph = self.graph
        if currentNode is None:
            currentNode = anchestorNode
        if alreadyVisited is None:
            alreadyVisited = []
        for child in list(pointGraph.successors(currentNode)):
            if (child not in alreadyVisited) and (child in similarityGraph):
                for otherConcept in list(similarityGraph.predecessors(child)):
                    if otherConcept != anchestorConcept:
                        self.__removeChildConceptSimilarToParentConcept(
                            otherConcept, anchestorConcept, anchestorNode, child, [child], ratio
                        )

    def __removeChildConceptSimilarToParentConcept(self, childConcept, parentConcept, node, child, visitedNodes, ratio=0.7):
        pointGraph = self.__ptGU.graph
        parentMembers = parentConcept.members
        childMembers = childConcept.members
        
        # 버그 수정: 비트 연산자(&) 결합 오류를 파이썬 논리 연산자(and) 구문으로 변경하여 연산 정합성 보장
        if len(childMembers) > 1 and len(parentMembers) > 4:
            tmp = list(set(parentMembers) & set(childMembers))
            if len(tmp) >= (len(parentMembers) - 1) * ratio:
                try:
                    pointGraph.remove_edge(node, visitedNodes[0])
                except Exception as e:  # 버그 수정: naked except를 명시적 예외 구문으로 다듬어 로깅 안전화
                    self.__logger.error('warning to be fixed: ' + str(e))
                parentConcept.removeMember(child.tokenID)
                return True
            return True
        elif len(childMembers) == 1:
            return False
        return True

    def __getSimilarNodes(self, node):
        """
        get nodes that share the same concept as the argument
        """
        similarityGraph = self.graph
        if node in similarityGraph:
            tmp_nodes = list(similarityGraph.predecessors(node))
            return set(similarityGraph.successors(tmp_nodes[0]))
        else:
            return []

    def __addSimilarNode(self, node, otherNode):
        """
        adds a node to the similar node graph. It also creates all required edges.
        """
        similarityGraph = self.graph
        if node not in similarityGraph:
            first_concept = ConceptNode(self.__ptGU.getMembersOfNodeInPointGraph(node))
        else:
            first_concept = list(similarityGraph.predecessors(node))[0]

        if otherNode not in similarityGraph:
            second_concept = ConceptNode(self.__ptGU.getMembersOfNodeInPointGraph(otherNode))
        else:
            second_concept = list(similarityGraph.predecessors(otherNode))[0]

        conceptToKeep = first_concept
        conceptToDelete = second_concept
        if len(first_concept.members) > len(second_concept.members):
            conceptToKeep = second_concept
            conceptToDelete = first_concept

        if conceptToKeep not in similarityGraph:
            similarityGraph.add_edge(NODE.CONCEPT, conceptToKeep)
        similarityGraph.add_edge(conceptToKeep, node)

        if (conceptToDelete != conceptToKeep) and (conceptToDelete in similarityGraph):
            for instanceNode in list(similarityGraph.successors(conceptToDelete)):
                similarityGraph.remove_edge(conceptToDelete, instanceNode)
                similarityGraph.add_edge(conceptToKeep, instanceNode)
            similarityGraph.remove_node(conceptToDelete)

        similarityGraph.add_edge(conceptToKeep, otherNode)

    def __refineSimilarNode(self, newConcept, node):
        """
        add refinement node to the similar node graph. It also modifies/creates all required edges.
        """
        similarityGraph = self.graph
        self.__logger.info('new concept found, ' + str(newConcept))
        if newConcept not in similarityGraph:
            similarityGraph.add_edge(NODE.CONCEPT, newConcept)
        if node in similarityGraph:
            old_concept = list(similarityGraph.predecessors(node))[0]
            similarityGraph.remove_edge(old_concept, node)
            similarityGraph.add_edge(newConcept, node)
            self.__logger.info('added, ' + str(newConcept))

    def __areNodesSimilar(self, node, otherNode, ratio):
        """
        determine if two nodes are similar: i.e. they have enough edges with the same label
        """
        if not node.usable or not otherNode.usable:
            return False
        node_members = self.__ptGU.getMembersOfNodeInPointGraph(node)
        otherNode_members = self.__ptGU.getMembersOfNodeInPointGraph(otherNode)
        if len(otherNode_members) < 2:
            otherNode.usable = False
            return False
        if len(node_members) < 2:
            node.usable = False
            return False
        if len(node_members) > len(otherNode_members):
            tmp = node_members
            node_members = otherNode_members
            otherNode_members = tmp

        count = 0
        if len(node_members) != len(otherNode_members):
            tmp1 = abs(len(node_members) - len(otherNode_members))
            tmp2 = len(node_members) * (1 - ratio)
            if tmp1 >= tmp2:
                return False

        for tokenID in node_members:
            if tokenID in otherNode_members:
                count += 1

        if len(otherNode_members) > 0:
            value = float(count) / float(len(otherNode_members))
            if value >= ratio:
                return True
        return False

    def __leafNodesInConcepts(self):
        """
        compute the number of leaf nodes that are present in all concepts
        """
        similarityGraph = self.graph
        concepts = list(similarityGraph.successors(NODE.CONCEPT))
        count = 0
        for concept in concepts:
            nodes = list(similarityGraph.successors(concept))
            if len(nodes) > 0:
                count += self.__computeAllLeafNodes(nodes[0])
        return count

    def __computeAllLeafNodes(self, node):
        similarityGraph = self.graph
        pointGraph = self.__ptGU.graph
        count = 0
        successors = list(pointGraph.successors(node))
        if len(successors) > 0:
            for successor in successors:
                if successor not in similarityGraph:
                    count += self.__computeAllLeafNodes(successor)
        else:
            count += 1
        return count

    def __howManyLeafNodesAreExplained(self, leafNodes):
        """
        determine how many leaf nodes are explained by concepts
        """
        count = 0
        for node in leafNodes:
            if self.__isExplainedByAConcept(node):
                count += 1
        return count

    def getUnexplainedLeafNodes(self, leafNodes):
        """
        determine how many leaf nodes are explained by concepts
        """
        if self.__unexplainedLeafNodes is None:
            self.__unexplainedLeafNodes = []
            for node in leafNodes:
                if not self.__isExplainedByAConcept(node):
                    self.__unexplainedLeafNodes.append(node.pointName)
        return self.__unexplainedLeafNodes

    def __isExplainedByAConcept(self, node):
        """
        determine whether a node can be explained by a concept: i.e. if there
        is at least a predecessor for which a concept has been identified
        """
        pointGraph = self.__ptGU.graph
        if node in self.graph:
            return True
        else:
            predecessors = list(pointGraph.predecessors(node))
            if len(predecessors) > 0:
                return self.__isExplainedByAConcept(predecessors[0])
        return False

    def addBaseClassToSimilarityGraph(self, foundBaseClasses):
        """
        replace relationships and adds a node to the similar node graph to
        take into account of derived classes
        """
        similarityGraph = self.graph
        for baseClass in foundBaseClasses:
            similarityGraph.add_edge(NODE.CONCEPT, baseClass)
            for derivedClass in foundBaseClasses[baseClass]:
                similarityGraph.add_edge(NODE.CONCEPT, derivedClass)
                concept = None
                for node in foundBaseClasses[baseClass][derivedClass]:
                    if node in similarityGraph:
                        concept = list(similarityGraph.predecessors(node))[0]
                        similarityGraph.remove_edge(concept, node)
                        if len(list(similarityGraph.successors(concept))) == 0:
                            similarityGraph.remove_edge(NODE.CONCEPT, concept)
                            similarityGraph.remove_node(concept)

                    similarityGraph.add_edge(derivedClass, node)

    @property
    def numberOfConcepts(self):
        if NODE.CONCEPT in self.graph:
            return len(list(self.graph.successors(NODE.CONCEPT)))
        return 0

    @property
    def numberOfUniquePoints(self):
        """
        returns the number of unique points across all clusters
        """
        return self.__leafNodesInConcepts()

    def printReportOnSimilarityGraph(self, leafNodes):
        similarityGraph = self.graph
        concepts = []
        if NODE.CONCEPT in similarityGraph:
            concepts = list(similarityGraph.successors(NODE.CONCEPT))

            self.__ptGU.saveToFile(similarityGraph)
            print('discovered ', len(concepts), ' concepts')
            print('to define all concepts you need to specify the meaning of ', self.__leafNodesInConcepts(), 'points')
            print('with this info ', self.__howManyLeafNodesAreExplained(leafNodes), 'points will be automatically defined')
            print('after this you will still have to indicate the meaning of ', len(leafNodes) - self.__howManyLeafNodesAreExplained(leafNodes), 'points')
        else:
            print('discovered ', len(concepts), ' concepts')

    def getInstancesOfConcept(self, concept):
        if concept in self.graph:
            return list(self.graph.successors(concept))
        else:
            return []
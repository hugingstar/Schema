# -*- coding: utf-8 -*-

import logging
import networkx as nx
import csv
import matplotlib.pyplot as plt

from inference.graphs.nodes.PointNode import TokenNode
from inference.graphs.nodes.PointNode import NODETYPE
from inference.classifier.device.ClassNameGuesser import ClassNameGuesser
from inference.configuration.configuration import CONFIG
from inference.graphs.Constants import NODE


class PointGraph:
    """
    this class encapsulates a collection of utilities for the creation of a
    graph out of point names and operations on it
    """

    def __init__(self, tokenizedPoints=None, classGuesserType='Basic'):
        self.__logger = logging.getLogger(__name__)
        self.__logger.info('initialization')
        self.__classGuesser = ClassNameGuesser()
        self.__classGuesserType = classGuesserType
        self.graph = None
        self.typesGraph = None
        self.leafNodes = {}
        self.__membersOfNode = {}

    @property
    def graph(self):
        return self.__graph

    @graph.setter
    def graph(self, graph):
        self.__graph = graph

    @property
    def typesGraph(self):
        return self.__typesGraph

    @typesGraph.setter
    def typesGraph(self, typesGraph):
        self.__typesGraph = typesGraph

    @property
    def leafNodes(self):
        return self.__leafNodes

    @leafNodes.setter
    def leafNodes(self, leafNodes):
        self.__leafNodes = leafNodes

    def createGraph(self, tokenizedPoints):
        """
        populates the graph with tokenNodes. It also takes care of populating
        the dictionary of leafNodes (which provides a fast lookup for leaf
        nodes in the PointGraph)
        """
        self.__logger.info('start creating token graph...')
        if tokenizedPoints is None:
            raise Exception('tokenizedPoint cannot be None')
        self.graph = nx.DiGraph()
        self.typesGraph = nx.DiGraph()
        leafNodes = {}
        self.__membersOfNode = {}
        counter = 0
        for pointName, point in sorted(tokenizedPoints.items()):
            if pointName != '':
                node_id = ''
                parent = None
                counter += 1
                for token in tokenizedPoints[pointName].tokens:
                    descendant = token.descendants
                    for desc in descendant:
                        node_id += desc.name
                        parent = self.__addNodeToGraph(node_id, desc.name,
                                                       pointName, parent)
                if parent is not None:
                    parent.nodeType = NODETYPE.POINT
                    leafNodes[parent] = parent
        self.leafNodes = leafNodes
        self.__logger.info('added ' + str(counter) + ' points')
        self.__logger.info('added ' + str(len(leafNodes)) + ' leaf nodes')
        self.__logger.info('...completed point graph')

    def __addNodeToGraph(self, nodeID, nodeName, pointName, parent=None):
        node = TokenNode(nodeID, nodeName, pointName=pointName)
        if node not in self.graph:
            if parent is None:
                self.graph.add_node(node)
            else:
                self.graph.add_edge(parent, node)
        self.typesGraph.add_edge(nodeName, node)
        return node

    @property
    def predessorNodesOfLeafs(self):
        setOfPredecessor = set()  # Python 3 대응: 내장 set 사용
        for node in self.leafNodes:
            # Python 3 대응: NetworkX Iterator 대응 list 변환
            setOfPredecessor.update(list(self.graph.predecessors(node)))
        return setOfPredecessor

    def printReportOnGraph(self):
        print('number of nodes', len(self.graph))
        print('number of leaf nodes', len(list(self.leafNodes.keys())))
        print('number of types', len(self.typesGraph) - len(self.graph))

    def saveToFile(self, similarityGraph):
        fileName = CONFIG.OUTPUTFOLDER + '/' + CONFIG.OBJECTFILE
        self.__logger.info('Writing objects file ' + fileName)
        # Python 3 대응: 'wb' 대신 인코딩 및 newline 옵션을 넣은 'w' 모드로 전환
        with open(fileName, 'w', encoding='utf-8', newline='') as cvsfile:
            csv_writer = csv.writer(cvsfile)

            column_header = ['concept', '#of instances', '#of children']
            csv_writer.writerow([column_header[0], column_header[1], column_header[2]])

            # Python 3 대응: NetworkX Iterator 대응 list 변환
            concepts = list(similarityGraph.successors(NODE.CONCEPT))
            chldrnPerConcept = {}
            for concept in concepts:
                nodes = list(similarityGraph.successors(concept))
                if len(nodes) > 0:
                    chldrnPerConcept = len(list(self.graph.successors(nodes[0])))
                    csv_writer.writerow([concept, len(nodes), chldrnPerConcept])
                else:
                    csv_writer.writerow([concept.nodeName, 0, -1])

            column_header = ['concept', 'nodes', '#children', 'children']
            csv_writer.writerow([column_header[0], column_header[1], column_header[2], column_header[3]])

            concepts = list(similarityGraph.successors(NODE.CONCEPT))
            children_per_concept = {}
            for concept in concepts:
                nodes = list(similarityGraph.successors(concept))
                if len(nodes) > -1:
                    for node in nodes:
                        children_per_concept = len(list(self.graph.successors(node)))
                        tmp = '\n['
                        for successor in list(self.graph.successors(node)):
                            tmp += str(successor)
                            tmp += ', \n'
                        tmp += ']'
                        if children_per_concept > -1:
                            csv_writer.writerow([concept, node, children_per_concept, tmp])

    def __saveSVGInstanceGraph(self):
        plt.figure()
        # 버그 방어 조치: 클래스 내부 정의와 일치하도록 명칭 통일 (self.graph 참조 백업)
        target_graph = self.graph if self.graph is not None else nx.DiGraph()
        G = target_graph.copy()
        pos = {}
        labels = {}
        nodes = []
        properties = []
        for node in G:
            if isinstance(node, TokenNode):
                labels[node] = node.tokenID
            elif isinstance(node, str):  # Python 3 대응: basestring -> str
                labels[node] = node

        # Python 3 대응: Iterator 대응 list 변환 일괄 적용
        for concept in list(G.successors(NODE.CONCEPT)):
            tmps = list(G.successors(concept))
            if len(tmps) > 0:
                for tmp in tmps:
                    if tmp.nodeType == NODETYPE.POINT:
                        properties.append(tmp)
                    else:
                        nodes.append(tmp)

        for node in nodes:
            props = list(self.__graph.successors(node))
            properties.extend(props)
            for prop in props:
                G.add_edge(node, prop)
                labels[prop] = prop.tokenID

        node_size = 100
        pos = self.__customLayout(NODE.CONCEPT,
                                  list(G.successors(NODE.CONCEPT)),
                                  nodes,
                                  properties,
                                  node_size)
        nx.draw_networkx_nodes(G, pos, nodelist=properties, node_color='y', node_size=node_size, alpha=0.8)
        nx.draw_networkx_nodes(G, pos, nodelist=[NODE.CONCEPT], node_color='g', node_size=node_size, alpha=0.8)
        nx.draw_networkx_nodes(G, pos, nodelist=list(G.successors(NODE.CONCEPT)), node_color='b', node_size=node_size, alpha=0.8)
        nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color='r', node_size=node_size, alpha=0.8)

        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)

        # 버그 수정: 정의되지 않은 내부 속성 호출부 안전화 및 라벨 출력 정합성 유지
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        plt.savefig("instances.svg")

    def __customLayout(self, root, branches, leafs, properties, node_size):
        node_distance = 4 * node_size
        pos = {}
        i = 0
        max_span = max([len(properties), len(branches), len(leafs)])

        center = float(max_span) / float(len(properties)) if len(properties) > 0 else 1.0
        start = 0
        for node in properties:
            pos[node] = (node_distance * 7.0 / 2.0, node_distance * center * (start + i))
            i += 1
        center = max_span / float(len(leafs)) if len(leafs) > 0 else 1.0
        start = 0
        i = 0
        for node in leafs:
            pos[node] = (node_distance * 5.0 / 2.0, node_distance * center * (start + i))
            i += 1
        center = max_span / float(len(branches)) if len(branches) > 0 else 1.0
        start = 0
        i = 0
        for node in branches:
            pos[node] = (node_distance * 3.0 / 2.0, node_distance * center * (start + i))
            i += 1
        center = max_span / 2.0
        start = 0
        pos[root] = (node_distance * 1.0 / 2.0, node_distance * center)
        return pos

    def findParentsOfSimilarTypes(self, node):
        """
        find all the nodes pointing to nodes of the same types
        """
        nodetype = list(self.typesGraph.predecessors(node))[0]
        nodes = list(self.typesGraph.successors(nodetype))
        tmp = []
        for n in nodes:
            tmp.extend(list(self.graph.predecessors(n)))
        return set(tmp)

    def findCommonEdges(self, node, otherNode):
        """
        find the number of edges that have the same label between two nodes
        """
        out_edges = list(self.graph.out_edges(node))
        other_out_edges = list(self.graph.out_edges(otherNode))
        count = 0
        for edge in out_edges:
            tokenID = edge[1].tokenID
            for otherEdge in other_out_edges:
                if tokenID == otherEdge[1].tokenID:
                    count += 1
        return count

    def areNodesSimilar(self, node, otherNode, ratio):
        """
        determine if two nodes are similar: i.e. they have enough edges with
        the same label
        """
        out_edges = list(self.graph.out_edges(node))
        other_out_edges = list(self.graph.out_edges(otherNode))
        count = 0
        if len(out_edges) != len(other_out_edges):
            if abs(len(out_edges) - len(other_out_edges)) >= len(out_edges) * (1 - ratio):
                return False

        for edge in out_edges:
            tokenID = edge[1].tokenID
            for otherEdge in other_out_edges:
                if tokenID == otherEdge[1].tokenID:
                    count += 1
                    break

        if len(out_edges) > 0:
            value = count / float(len(out_edges))
            if value >= ratio:
                return True
        return False

    def getMembersOfNodeInPointGraph(self, node):
        """
        gets all the members (tokens of a node in pointgraph)
        """
        if node not in self.__membersOfNode:
            members = []
            if node in self.graph:
                out_edges = list(self.graph.out_edges(node))
                for edge in out_edges:
                    members.append(edge[1].tokenID)
                self.__membersOfNode[node] = members
                return members
            else:
                msg = f"Node: {node} not in graph"
                raise Exception(msg)
        else:
            return self.__membersOfNode[node]

    def getDescendantsOfNode(self, node, branchNode=None, descendants=None):
        if descendants is None:
            descendants = {}
        if branchNode is None:
            branchNode = node
            descendants[branchNode] = []

        successors = list(self.graph.successors(node))
        if len(successors) == 0:
            return descendants

        elif len(successors) > 1 or node.nodeType == NODETYPE.POINT:
            tmp = descendants[branchNode]
            if not node.nodeType == NODETYPE.POINT:
                del descendants[branchNode]
            for child in successors:
                if child not in descendants:
                    descendants[child] = []
                    descendants[child].extend(tmp)
                    descendants[child].append(child)
                    self.getDescendantsOfNode(child, child, descendants)
            return descendants

        elif len(successors) == 1:
            child = successors[0]
            descendants[branchNode].append(child)
            return self.getDescendantsOfNode(child, branchNode, descendants)
# -*- coding: utf-8 -*-

import math
import subprocess
import logging
from networkx import DiGraph

from inference.configuration.configuration import CONFIG
from inference.classifier.Constants import CONSTANTS
from inference.graphs.Constants import NODE
import inference.classifier.device.ClassNameGuesser as ClassNameGuesser
from inference.graphs.nodes.PointNode import ConceptNode
from inference.classifier.RulesConstants import KEYS as classKEY
from inference.graphs.Constants import EdgeType


class SemanticGraph:
    """
    this class encapsulates a collection of utilities for the creation and
    manipulation of a semantic graph
    """
    __classGuesserType = 'Basic'

    def __init__(self, pointGraph, similarityGraph, classGuesserType='Basic'):
        self.__logger = logging.getLogger(__name__)
        self.__logger.info('initialization')
        self.__classGuesser = ClassNameGuesser.ClassNameGuesser()
        self.__classGuesserType = classGuesserType
        self.__pointGraph = pointGraph
        self.__similarityGraph = similarityGraph
        self.graph = None

    @property
    def graph(self):
        return self.__graph

    @graph.setter
    def graph(self, graph):
        self.__graph = graph

    def findDerivationRelationships(self, ratio1, ratio2):
        """
        analyzes a semantic graph and attempts to identify derivation
        relationships among classes
        """
        self.__logger.info('starting findDerivationRelationships')
        derivation = {}
        derivedClasses = {}
        for node in self.graph:
            for otherNode in self.graph:
                if node != otherNode:
                    if not (node in self.graph[otherNode] or otherNode in self.graph[node]):
                        if not self.__areNodesDerivationOfSameBase(node, otherNode):
                            if not self.__areNodesRelatives(node, otherNode):
                                if node.isGeneralizationOf(otherNode, ratio1):
                                    if node not in derivation:
                                        derivation[node] = []
                                    derivation[node].append(otherNode)   
                                elif node.isDerivedFrom(otherNode):
                                    if otherNode not in derivation:
                                        derivation[otherNode] = []
                                    derivation[otherNode].append(node)   
                                else:
                                    commonNodes = node.findCommonMembers(otherNode, ratio2)
                                    if len(commonNodes) > 0:
                                        baseClass = ConceptNode(commonNodes)
                                        # create a name for the new base class:
                                        if node.nodeName == otherNode.nodeName:
                                            baseClass.nodeName = otherNode.nodeName
                                        else:
                                            baseClass.setNodeName(node.nodeName + '_' + otherNode.nodeName)
                                        if baseClass not in derivedClasses:
                                            derivedClasses[baseClass] = []
                                        if baseClass != node:
                                            derivedClasses[baseClass].append(node)
                                        if baseClass != otherNode:
                                            derivedClasses[baseClass].append(otherNode) 
                                    
        # Python 3 대응: 로깅 인자 포맷 버그를 f-string 형태로 완전 수정
        self.__logger.info(f'found {len(derivation)} new derived classes')
        for baseClass in derivation:
            self.__addDerivedNodeToSemanticGraph(derivation[baseClass], baseClass) 
        for baseClass in derivedClasses:
            self.__addBaseNodeToSemanticGraph(derivedClasses[baseClass], baseClass)
                     
    def __areNodesDerivationOfSameBase(self, node, otherNode):
        """
        checks whether the two nodes are already a derivation of a common parent
        """         
        # Python 3 대응: NetworkX 2.x 이터레이터 리스트화
        for parent in list(self.graph.predecessors(node)):            
            if 'type' in self.graph[parent][node]: 
                if self.graph[parent][node]['type'] == 'derivation':
                    if parent in list(self.graph.predecessors(otherNode)):
                        if 'type' in self.graph[parent][otherNode]:
                            if self.graph[parent][otherNode]['type'] == 'derivation':
                                return True        
        return False
    
    def __areNodesRelatives(self, node, otherNode):
        """
        checks whether the two nodes are derive one from each other
        """         
        out = self.__isNodeDeriveredFrom(node, otherNode)
        out1 = self.__isNodeDeriveredFrom(otherNode, node)
        output = out and out1        
        return output
                     
    def __isNodeDeriveredFrom(self, node, otherNode):
        """
        checks whether the two nodes are derive one from each other
        """          
        if node not in self.graph[otherNode]:
            return False
        
        # Python 3 대응: NetworkX 2.x 이터레이터 리스트화
        parents = list(self.graph.predecessors(node))
        if otherNode in parents:
            if 'type' in self.graph[otherNode][node]: 
                if self.graph[otherNode][node]['type'] == 'derivation':
                    return True        
        return False     
       
    def saveSemanticGraphImage(self, TokenSetOfClasses=None):         
        filename = CONFIG.OUTPUTFOLDER + '/' + CONFIG.SEMANTICGRAPH
        self.__saveDOTDirectedGraph(filename, TokenSetOfClasses)

    def inferSemanticGraph(self):
        """
        attempts at inferring the semantic model of the point names
        """
        labels = {}
        semanticGraph = DiGraph()
        self.graph = semanticGraph
        similarityGraph = self.__similarityGraph.graph
        
        # Python 3 대응: NetworkX 2.x 이터레이터 리스트화
        for concept in list(similarityGraph.successors(NODE.CONCEPT)):
            # add concept to semantic graph
            semanticGraph.add_node(concept)          
            labels[concept] = concept
            # get all the instances of a concept
            nodes = list(similarityGraph.successors(concept))            
            users_of_concept = []
            for node in nodes:
                users_of_concept.extend(self.__findConceptThatInstantiateCurrentOne(node, node.tokenID))
            
            # Python 3 대응: 구형 Set을 기본 내장 set으로 수정
            users_of_concept = set(users_of_concept)
            for user in users_of_concept:
                semanticGraph.add_edge(user, concept, {EdgeType.KEY: EdgeType.ASSOCIATION})
        
    def __handleDerivation(self):
        """
        handles all the operations to detect derived classes and to add them
        to the semantic graph
        """
        similarityGraph = self.__similarityGraph.graph
        foundBaseClasses = {}
        
        # Python 3 대응: NetworkX 2.x 이터레이터 리스트화
        for concept in list(similarityGraph.successors(NODE.CONCEPT)):                       
            nodes = list(similarityGraph.successors(concept))
            # find simple derivation/specialization relationships
            baseClass, derivedClasses = self.__findSimpleDerivedClasses(nodes)
            if baseClass is not None:
                foundBaseClasses[baseClass] = derivedClasses
            
        for baseClass in foundBaseClasses:            
            for derivedClass in foundBaseClasses[baseClass]:                
                # if the derived class was already in the semantic graph, update the relationship
                try:
                    self.graph.remove_edge(derivedClass, baseClass) 
                except Exception:
                    pass
                self.__addDerivedNodeToSemanticGraph([derivedClass], baseClass)            
        self.__similarityGraph.addBaseClassToSimilarityGraph(foundBaseClasses)
                   
    def __addBaseNodeToSemanticGraph(self, derivedClasses, baseClass):
        """
        adds a base class to the semantic graph and updates the relationship
        """
        # add the base class and derivation relationship to derived classes        
        self.__addDerivedNodeToSemanticGraph(derivedClasses, baseClass)
        # updates association relationship        
        for derivedClass in derivedClasses:
            # Python 3 대응: NetworkX 2.x 이터레이터 리스트화
            for child in list(self.graph.successors(derivedClass)):
                if child.nodeName in baseClass.members:
                    if 'type' in self.graph[derivedClass][child]:
                        if self.graph[derivedClass][child][EdgeType.KEY] == EdgeType.ASSOCIATION:                            
                            self.graph.remove_edge(derivedClass, child)
                            self.graph.add_edge(baseClass, child, {EdgeType.KEY: EdgeType.ASSOCIATION})
    
    def __addDerivedNodeToSemanticGraph(self, derivedClasses, baseClass):
        """
        adds derived classes to the semantic graph and updates the relationship
        """     
        for derivedClass in derivedClasses:
            self.graph.add_edge(baseClass, derivedClass, {EdgeType.KEY: EdgeType.DERIVATION})             
            # get edges of base class (Python 3 대응 리스트화)
            for node in list(self.graph.successors(baseClass)):
                if node in list(self.graph.successors(derivedClass)):
                    if 'type' in self.graph[derivedClass][node]:
                        if self.graph[derivedClass][node][EdgeType.KEY] == EdgeType.ASSOCIATION:
                            self.graph.remove_edge(derivedClass, node)

    def __findSimpleDerivedClasses(self, similarNodes):
        """
        find simple derivation/specialization relationships
        returns the base class and a dictionary listing for each derived class
        all of its instances
        """
        candidate_nodes = []
        derivedNodes = {}
        derivedClasses = {}
        baseClass = None
        tmpChild = None
        
        if len(similarNodes) <= 1:
            return None, None
            
        # get all similar nodes with one child (Python 3 대응 리스트화)       
        for node in similarNodes:
            children = list(self.__pointGraph.graph.successors(node))
            if len(children) == 1:                
                if not children[0].tokenID.isdigit():
                    tmpChild = children[0]
                    candidate_nodes.append(node)
            else:
                return None, None
        if tmpChild is None:
            return None, None
            
        members = [tmpChild.tokenID]
        baseClass = ConceptNode(members, tmpChild.tokenID)                
        for node in candidate_nodes:
            tokenID = node.tokenID
            if not tokenID.isdigit():
                if tokenID not in derivedNodes:
                    derivedNodes[tokenID] = []
                derivedNodes[tokenID].append(node)

        if len(list(derivedNodes.keys())) <= 1:
            return None, None
        
        for key in derivedNodes:
            members = [derivedNodes[key][0].tokenID]
            members.extend(self.__pointGraph.getMembersOfNodeInPointGraph(derivedNodes[key][0]))
            derivedClass = ConceptNode(members, key) 
            derivedClass.setNodeName(derivedNodes[key][0].tokenID)
            derivedClasses[derivedClass] = derivedNodes[key]
               
        return baseClass, derivedClasses  
  
    def __findConceptThatInstantiateCurrentOne(self, currentNode, currentToken):
        """
        attempts to find relationships like containment, etc.
        """  
        # Python 3 대응: NetworkX 2.x 이터레이터 리스트화
        users_of_concept = list(self.__pointGraph.graph.predecessors(currentNode))
        output = []        
        if len(users_of_concept) == 0:
            return output
        else:
            for parent in users_of_concept:
                if parent in self.__similarityGraph.graph:
                    concept = list(self.__similarityGraph.graph.predecessors(parent))[0]
                    if concept.hasMember(currentToken):
                        direct_concept = self.__findBaseConceptWithMember(concept, currentToken)
                        if direct_concept is not None:
                            output.append(direct_concept)
                else:
                    output.extend(self.__findConceptThatInstantiateCurrentOne(parent, currentToken))            
            return output
    
    def __findBaseConceptOf(self, concept):
        if concept in self.graph:
            parents = list(self.graph.predecessors(concept))
            if len(parents) > 0:
                parent = parents[0]
                return self.__findBaseConceptOf(parent)            
        return concept 
    
    def __findBaseConceptWithMember(self, concept, member, visited=None):
        """
        return the base class that has an association relationship with the
        current concept
        """
        if visited is None:
            visited = []
        visited.append(concept)
        if concept.hasMember(member):        
            if concept in self.graph:
                parents = list(self.graph.successors(concept))
                if len(parents) > 0:
                    parent = parents[0]
                    if not parent.hasMember(member):
                        return concept
                    elif parent in visited:
                        return concept
                    else:
                        return self.__findBaseConceptWithMember(parent, member, visited)                        
            return concept 
        raise NameError(member + ' not in concept ')

    def __layoutForSemanticGraph(self, G):        
        pos = nx.circular_layout(G)        
        for node in G:
            if G.in_degree(node) == 0:
                tmp = pos[node]
                tmp[1] = tmp[1] * 5
                pos[node] = tmp
            elif G.out_degree(node) == 0:
                tmp = pos[node]
                tmp[1] = tmp[1] / 3.0
                pos[node] = tmp
            else:
                degree = G.degree(node)
                tmp = pos[node]
                tmp[1] = tmp[1] * math.log(degree)                
        return pos
    
    def __computeNumberOfInstancesOfClasses(self):
        """
        count the number of instances for each class
        """
        for node in list(self.graph.nodes()):
            if node in self.__similarityGraph.graph:
                tmp = len(list(self.__similarityGraph.graph.successors(node)))
                node.numberOfInstances = tmp
                
    def __saveDOTDirectedGraph(self, graphName, TokenSetOfClasses=None):
        # Python 3 대응: 명시적 인코딩 인자 추가 오픈
        output = open(graphName + '.dot', 'w', encoding='utf-8')
        self.__computeNumberOfInstancesOfClasses()
        pointCluster = False
        equipmentCluster = {}
        if TokenSetOfClasses is not None:
            pointCluster = True
            
        subgraph = []
        equipmentGraph = []
        if pointCluster:
            subgraph.append('\tsubgraph cluster0 { \n')
            subgraph.append('\t\tstyle=filled;\n')
            subgraph.append('\t\tcolor=lightgrey;\n')
            subgraph.append('\t\tnode [style=filled,color=white];\n')
            subgraph.append('\t\tlabel = "non_devices";\n')
                     
        tmp = 'digraph {\n'
        nodes_names = ''
        tmp1 = ''
        for node in self.graph:
            scale = ''
            if node.numberOfInstances > 0:                
                scale = str(1.6 + math.log(node.numberOfInstances))
            else:
                scale = '1.6'
                
            if pointCluster: 
                if (node in TokenSetOfClasses and len(TokenSetOfClasses[node]) <= 3) or node not in TokenSetOfClasses:
                    subgraph.append('\t\t\t"' + node.nodeID + '" [shape=ellipse,width=' + scale + ', label="' + node.nodeName + '"]\n')
                else:
                    if node.classLabel not in equipmentCluster:
                        equipmentCluster[node.classLabel] = []
                    equipmentCluster[node.classLabel].append(node)                                
            else:
                nodes_names += '\t\t"' + node.nodeID + '" [shape=ellipse,width=' + scale + ', label="' + node.nodeName + '"]\n'
            
            for successor in list(self.graph.successors(node)):
                if self.graph[node][successor]['type'] == 'association':
                    tmp1 += '\t\t"' + node.nodeID + '" -> "' + successor.nodeID + '" [dir=back color="red" arrowtail="odiamond" arrowsize="1.5"]\n'
                elif self.graph[node][successor]['type'] == 'contains':                
                    tmp1 += '\t\t"' + node.nodeID + '" -> "' + successor.nodeID + '" [dir=back color="black" arrowsize="1.5"]\n'
                elif self.graph[node][successor]['type'] == 'derivation':                
                    tmp1 += '\t\t"' + node.nodeID + '" -> "' + successor.nodeID + '" [dir=back color="blue" arrowsize="1.5" arrowtail="onormal"]\n'
                
        if pointCluster:
            subgraph.append('\t\t}\n')
            for classLabel in list(equipmentCluster.keys()):
                equipmentGraph.append('\tsubgraph cluster' + classLabel + ' { \n')
                equipmentGraph.append('\t\tstyle=filled;\n')
                equipmentGraph.append('\t\tcolor=lightgrey;\n')
                equipmentGraph.append('\t\tnode [style=filled,color=white];\n')
                equipmentGraph.append('\t\tlabel = "' + classLabel + '";\n')
                for node in equipmentCluster[classLabel]:
                    equipmentGraph.append('\t\t\t"' + node.nodeID + '" [shape=ellipse,width=' + scale + ', label="' + node.nodeName + '"]\n')
                equipmentGraph.append('\t\t}\n')
                
        subgraph = ''.join(subgraph)
        equipmentGraph = ''.join(equipmentGraph)
            
        tmp += subgraph + equipmentGraph + nodes_names + tmp1 + '}'
        output.write(tmp)
        output.close()
        # call dot to generate the graph (Python 3 파일 핸들러 호환 인코딩 지정 조치)
        cmd = ['dot', '-Tsvg', graphName + '.dot']
        with open(graphName + '.svg', "w", encoding='utf-8') as outfile:
            subprocess.call(cmd, stdout=outfile)

    def getTokenSetOfClasses(self,
                             min_number=CONFIG.MEMBERNUMBERRELEVANTCLASSES,
                             max_number=CONFIG.MAXMEMBERNUMBERRELEVANTCLASSES):
        """
        returns a dictionary of dictionary, containing for each class and
        member in class the set of tokens.
        """
        result = {}
        similarityGraph = self.__similarityGraph.graph
        for concept in self.graph:
            mnumb = len(concept.members)
            if int(min_number) <= mnumb <= int(max_number):                
                if concept in similarityGraph:
                    if len(list(similarityGraph.successors(concept))) > 0:
                        node = list(similarityGraph.successors(concept))[0]
                        descendants = self.__pointGraph.getDescendantsOfNode(node)
                        result[concept] = []
                        for child in descendants:
                            tmp = []
                            tmp1 = []
                                
                            for tokenNode in descendants[child]:
                                tmp.append(tokenNode)  
                                tmp1.append(tokenNode.tokenID)  
                            result[concept].append(tmp1) 
                            concept.addPoint(tmp, CONSTANTS.UNKNOWNLABEL, 0)               
        return result  
        
    def saveTokenSetOfClasses(self, tokenSet, classesToSave=None, datasetName=''):
        filename = CONFIG.OUTPUTFOLDER + '/' + str(datasetName) + '_' + CONFIG.CLASSTOKENFILE
        
        # Python 3 대응: 파일 오픈 시 인코딩 추가
        outputFile = open(filename, 'w', encoding='utf-8')
        self.__logger.info('opening ' + filename + ' to write...')
        out = '{\n\t"' + classKEY.CLASSES + '":[\n'
        if classesToSave is None:
            classesToSave = list(tokenSet.keys())
        outputFile.write(out)
        for n, classtype in enumerate(classesToSave):    
            if classtype in tokenSet:
                out = '\t\t{'
                out += '\n\t\t\t"' + classKEY.LABEL + '":"' + classtype.classLabel + '",\n'
                out += '\t\t\t"id":' + str(classtype.nodeID) + ',\n'
                out += '\t\t\t"#instances":' + str(classtype.numberOfInstances) + ',\n'
                out += '\t\t\t"instances":"'
                for instance in classtype.instances:
                    out += str(instance.nodeID) + ','
                out += '",\n'
                
                out += '\t\t\t"' + classKEY.POINTS + '":[\n'
                
                points = classtype.points   
                for i, pointset in enumerate(list(points.keys())):
                    if i:
                        out += ',\n'   
                    out += '\t\t\t\t{"' + classKEY.POINT + '":["'
                    out += '","'.join(map(str, pointset))                    
                    out += '"], "' + classKEY.LABEL + '":"' + points[pointset][0] + '", "likelihood":"' + str(points[pointset][1]) + '"}'
                out += '\n\t\t\t\t]\n'
                if n == len(classesToSave) - 1:
                    out += '\t\t}\n'
                else:
                    out += '\t\t},\n'
                outputFile.write(out)
        out = '\t]\n}'
        outputFile.write(out)
        outputFile.close()
        self.__logger.info(filename + ' written...')

    @property
    def baseClasses(self):
        """
        gets all the base classes in semanticGraph
        """ 
        baseClasses = set()  # Python 3 대응: 내장 set 사용
        for concept in self.graph:
            is_base = True
            for other in list(self.graph.predecessors(concept)):
                if EdgeType.KEY in self.graph[other][concept]:
                    if self.graph[other][concept][EdgeType.KEY] == EdgeType.DERIVATION:
                        is_base = False
            if is_base:
                baseClasses.add(concept)
        return baseClasses
    
    @property      
    def instancesOfBaseClasses(self):
        output = {}
        alreadyVisited = []
        for baseClass in self.baseClasses:
            output = self.getInstancesOfClass(baseClass, output=output, alreadyVisited=alreadyVisited)
        return output

    def getInstancesOfClass(self, currentClass, output=None, alreadyVisited=None):
        if output is None:        
            output = {}
        if alreadyVisited is None:
            alreadyVisited = []
        if currentClass in self.graph:
            if currentClass not in alreadyVisited:
                alreadyVisited.append(currentClass)
                output[currentClass] = [set(), []]  # Python 3 대응 set 사용
                output[currentClass][0].update(self.__similarityGraph.getInstancesOfConcept(currentClass))
                for derivedClass in self.getAllDerivedClassesOfClass(currentClass):
                    if derivedClass not in alreadyVisited:
                        output[currentClass][1].append(self.getInstancesOfClass(derivedClass, alreadyVisited=alreadyVisited))
                        alreadyVisited.append(derivedClass)
        return output        
    
    def getAllDerivedClassesOfClass(self, currentClass, derivedClasses=None):        
        if derivedClasses is None:
            derivedClasses = set()  # Python 3 대응 set 사용
         
        if currentClass in self.graph:
            for other in list(self.graph.successors(currentClass)):
                if EdgeType.KEY in self.graph[currentClass][other]:
                    if self.graph[currentClass][other][EdgeType.KEY] == EdgeType.DERIVATION:                        
                        if other in derivedClasses:                            
                            return derivedClasses
                        else:                            
                            derivedClasses.add(other)
                            self.getAllDerivedClassesOfClass(other, derivedClasses)
      
        return derivedClasses

    def reportOnBaseClassesUsage(self):
        """
        generates a report of the usage of bases classes.
        """  
        record = self.instancesOfBaseClasses
        for baseClass in record:
            baseClass.numberOfInstances = len(record[baseClass][0])
            baseClass.instances = record[baseClass][0]
            out = ''
            for child_record in record[baseClass][1]:
                report = ''
                out += self.__reportOnInstancesOfDerivedClass(child_record, report)
            if out != '':
                self.__logger.info(out)

    def __reportOnInstancesOfDerivedClass(self, record, rept, indent='\t'):
        for currClass in record:
            currClass.numberOfInstances = len(record[currClass][0])
            currClass.instances = record[currClass][0]
            if len(currClass.members) >= 4:
                rept += (indent + 'derived class->name ' +
                         currClass.nodeName +
                         ' label:' + currClass.classLabel +
                         ' ID:' + str(currClass.nodeID) +
                         ' #instances ' + str(len(record[currClass][0])) + '\n'
                         )
                indent += '\t'
                for child_record in record[currClass][1]:
                    for child in child_record:
                        tmp = ''
                        rept += self.__reportOnInstancesOfDerivedClass(child_record, tmp, indent)
        return rept

    def getSummaryOfClasses(self):
        """
        generates a report of the usage of labelled classes.
        """
        summary = {}
        for concept in self.graph:
            classLabel = concept.classLabel
            if classLabel != '':
                if classLabel not in summary:
                    summary[classLabel] = set()  # Python 3 대응 set 사용
                instances = self.getAllInstancesOfClass(concept)
                summary[classLabel].update(instances)

        for classLabel in summary:
            self.__logger.info(classLabel + str(len(summary[classLabel])))
        return summary

    def getAllInstancesOfClass(self, currentClass):
        """
        returns a set of all the instances of currentClass
        """
        output = set()  # Python 3 대응 set 사용
        if currentClass in self.graph:
            output.update(self.__similarityGraph.getInstancesOfConcept(currentClass))
            currentClass.numberOfInstances = len(output)
            currentClass.instances = output
        return output
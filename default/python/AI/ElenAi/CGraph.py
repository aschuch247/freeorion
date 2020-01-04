"""
A graph represents a set of nodes and edges.

The used algorithms do neither support negative edge costs nor cycles. A node identifier must not be -1.
"""

from ElenAi.CGraphRouter import CGraphRouter


class CGraph(object):


    def __init__(self):
        self.m_dictGraphNode = dict()


    def vAdd(self, ixGraphNode):
        self.m_dictGraphNode[ixGraphNode] = dict()


    def vLink(self, ixGraphNodeFrom, ixGraphNodeTo, fCost):
        self.m_dictGraphNode[ixGraphNodeFrom][ixGraphNodeTo] = fCost


    def fGetCost(self, tixGraphNode):
        fCost = 0
        ixGraphNodeFrom = -1

        for ixGraphNode in tixGraphNode:
            if (ixGraphNodeFrom == -1):
                ixGraphNodeFrom = ixGraphNode
                continue

            fCost += self.m_dictGraphNode[ixGraphNodeFrom][ixGraphNode]

            ixGraphNodeFrom = ixGraphNode

        return fCost


    def oGetGraphRouter(self, ixGraphNodeFrom):
        """
        This method implements the Dijkstra algorithm.
        @todo Always use the shortest route on supply lines, but decide to use the least jumps outside supply lines.
        """

        listGraphNode = self.m_dictGraphNode.keys()
        dictCost = dict()
        dictGraphNodePrevious = dict()

        for ixGraphNode in listGraphNode:
            dictCost[ixGraphNode] = float('inf')
            dictGraphNodePrevious[ixGraphNode] = -1

        dictCost[ixGraphNodeFrom] = 0

        while listGraphNode:
            ixGraphNodeMin = listGraphNode[0]
            fCostMin = dictCost[ixGraphNodeMin]

            for i in range(1, len(listGraphNode)):
                if (dictCost[listGraphNode[i]] < fCostMin):
                    ixGraphNodeMin = listGraphNode[i]
                    fCostMin = dictCost[ixGraphNodeMin]

            listGraphNode.remove(ixGraphNodeMin)

            for i in self.m_dictGraphNode[ixGraphNodeMin]:
                if i in listGraphNode:
                    fCostAlternative = dictCost[ixGraphNodeMin] + self.m_dictGraphNode[ixGraphNodeMin][i]
                    if (fCostAlternative < self.m_dictGraphNode[i]):
                        dictCost[i] = fCostAlternative
                        dictGraphNodePrevious[i] = ixGraphNodeMin

        return CGraphRouter(dictGraphNodePrevious, dictCost)

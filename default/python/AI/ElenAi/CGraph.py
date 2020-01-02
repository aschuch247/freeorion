"""
A graph represents a set of nodes and edges.
"""


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

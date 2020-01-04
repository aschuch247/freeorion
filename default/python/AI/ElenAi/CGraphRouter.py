"""
The graph router knows all paths from a given starting node to any other (reachable) node.
"""


class CGraphRouter(object):


    def __init__(self, dictGraphNodePrevious, dictCost):
        self.m_dictGraphNodePrevious = dictGraphNodePrevious
        self.m_dictCost = dictCost


    def tixGetPath(self, ixGraphNodeTo):
        """
        Get the path to the given graph node. The first element in the returned path is the source graph node and the
        last element in the path is the destination graph node.
        """

        if (self.m_dictGraphNodePrevious[ixGraphNodeTo] == -1):
            return None

        tixGraphNodePath = [ixGraphNodeTo]

        while self.m_dictGraphNodePrevious[ixGraphNodeTo] != -1:
            ixGraphNodeTo = self.m_dictGraphNodePrevious[ixGraphNodeTo]
            tixGraphNodePath.append(ixGraphNodeTo)

        tixGraphNodePath.reverse()

        return tixGraphNodePath


    def ixGetClosestGraphNode(self, setGraphNode):
        ixGraphNodeMin = None
        fCostMin = float('inf')

        for ixGraphNode in setGraphNode:
            if (self.m_dictCost[ixGraphNode] < fCostMin):
                ixGraphNodeMin = ixGraphNode
                fCostMin = self.m_dictCost[ixGraphNode]

        return ixGraphNodeMin


    def tixGetReachableGraphNode(self):
        for ixGraphNode, fCost in self.m_dictCost.items():
            if (fCost < float('inf')):
                yield ixGraphNode

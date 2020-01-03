"""
The graph router knows all paths from a given starting node to any other (reachable) node.
"""


class CGraphRouter(object):


    def __init__(self, dictGraphNodePrevious):
        self.m_dictGraphNodePrevious = dictGraphNodePrevious


    def tixGetPath(self, ixGraphNodeTo):
        if (self.m_dictGraphNodePrevious[ixGraphNodeTo] == -1):
            return None

        tixGraphNodePath = [ixGraphNodeTo]

        while self.m_dictGraphNodePrevious[ixGraphNodeTo] != -1:
            ixGraphNodeTo = self.m_dictGraphNodePrevious[ixGraphNodeTo]
            tixGraphNodePath.append(ixGraphNodeTo)

        tixGraphNodePath.reverse()

        return tixGraphNodePath

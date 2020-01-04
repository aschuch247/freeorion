"""
The graph advisor can reject a given node from being considered for routing.
"""


class CGraphAdvisor(object):


    def __init__(self, tixGraphNode):
        self.m_tixGraphNode = tixGraphNode


    def bShallIgnore(self, ixGraphNode):
        return ixGraphNode in self.m_tixGraphNode

"""
The research tree contains all technologies and can be used to research a technology along with all its prerequisites.

The nodes of the graph are the technologies, the edges lead to the the prerequisites. Searching the tree happens by
starting at the technology to research and then getting a list of all the prerequisites.
"""

from ElenAi.CGraph import CGraph


class CResearchTree(CGraph):


    def __init__(self):
        super(CResearchTree, self).__init__()

        self.m_dictIndexToTechnology = dict()
        self.m_dictTechnologyToIndex = dict()


    def vAddTechnology(self, ixTechnology, sTechnology):
        self.m_dictIndexToTechnology[ixTechnology] = sTechnology
        self.m_dictTechnologyToIndex[sTechnology] = ixTechnology

        super(CResearchTree, self).vAdd(ixTechnology)


    def vLinkTechnology(self, ixTechnology, ixTechnologyPrerequiste):
        super(CResearchTree, self).vLink(ixTechnology, ixTechnologyPrerequiste, 1.0)


    def sGetTechnology(self, ixTechnology):
        return self.m_dictIndexToTechnology[ixTechnology]


    def ixGetTechnology(self, sTechnology):
        return self.m_dictTechnologyToIndex[sTechnology]

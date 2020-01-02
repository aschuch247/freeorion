"""
This is a representation of the (known) universe.
"""

from ElenAi.CGraph import CGraph


class CUniverse(object):
    def __init__(self):
        self.m_oGraph = CGraph()
        self.m_dictSystem = dict()


    def vAddSystem(self, ixSystem, oSystem):
        self.m_oGraph.vAdd(ixSystem)
        self.m_dictSystem[ixSystem] = oSystem


    def vLinkSystem(self, ixSystemFrom, ixSystemTo):
        oSystemFrom = self.m_dictSystem[ixSystemFrom]
        oSystemTo = self.m_dictSystem[ixSystemTo]

        fDistance = ((oSystemFrom.fGetX() - oSystemTo.fGetX()) ** 2 + (oSystemFrom.fGetY() - oSystemTo.fGetY()) ** 2) ** 0.5

        self.m_oGraph.vLink(ixSystemFrom, ixSystemTo, fDistance)


    def fGetStarlaneDistance(self, tixSystem):
        return self.m_oGraph.fGetCost(tixSystem)

"""
This is a representation of the (known) universe.
"""

from ElenAi.CGraph import CGraph


class CUniverse(CGraph):


    def __init__(self):
        super(CUniverse, self).__init__()

        self.m_dictSystem = dict()


    def vAddSystem(self, oSystem):
        ixSystem = oSystem.ixGetSystem()

        self.m_dictSystem[ixSystem] = oSystem

        super(CUniverse, self).vAdd(ixSystem)


    def vLinkSystem(self, ixSystemFrom, ixSystemTo):
        oSystemFrom = self.m_dictSystem[ixSystemFrom]
        oSystemTo = self.m_dictSystem[ixSystemTo]

        fDistance = ((oSystemFrom.fGetX() - oSystemTo.fGetX()) ** 2 + (oSystemFrom.fGetY() - oSystemTo.fGetY()) ** 2) ** 0.5

        super(CUniverse, self).vLink(ixSystemFrom, ixSystemTo, fDistance)

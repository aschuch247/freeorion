"""
This is a representation of the (known) universe.
"""

from __future__ import print_function

from ElenAi.CGraph import CGraph


class CUniverse(CGraph):


    def __init__(self):
        super(CUniverse, self).__init__()

        self.__m_dictSystem = dict()


    def vAddSystem(self, oSystem):
        ixSystem = oSystem.ixGetSystem()

        self.__m_dictSystem[ixSystem] = oSystem

        super(CUniverse, self).vAdd(ixSystem)


    def vLinkSystem(self, ixSystemFrom, ixSystemTo):
        oSystemFrom = self.__m_dictSystem[ixSystemFrom]
        oSystemTo = self.__m_dictSystem[ixSystemTo]

        fDistance = ((oSystemFrom.fGetX() - oSystemTo.fGetX()) ** 2 + (oSystemFrom.fGetY() - oSystemTo.fGetY()) ** 2) ** 0.5

        super(CUniverse, self).vLink(ixSystemFrom, ixSystemTo, fDistance)


    def oGetSystem(self, ixSystem):
        return self.__m_dictSystem[ixSystem]


    def toGetSystem(self):
        for ixSystem, oSystem in self.__m_dictSystem.items():
            yield oSystem


    def vDump(self):
        print('--- universe ---')

        for oSystem in self.toGetSystem():
            for oPlanet in oSystem.toGetPlanet():
                if (oPlanet.bIsNative()):
                    print(
                        'Planet %d is a colony of native species \'%s\' (%.2f).' % (
                            oPlanet.ixGetPlanet(),
                            oPlanet.sGetSpecies(),
                            oPlanet.fGetPopulation()
                        )
                    )
                elif (oPlanet.bIsColony()):
                    print(
                        'Planet %d is a colony of species \'%s\' (%.2f) owned by empire %d.' % (
                            oPlanet.ixGetPlanet(),
                            oPlanet.sGetSpecies(),
                            oPlanet.fGetPopulation(),
                            oPlanet.ixGetEmpire()
                        )
                    )
                elif (oPlanet.bIsOutpost()):
                    print(
                        'Planet %d is an outpost owned by empire %d.' % (
                            oPlanet.ixGetPlanet(),
                            oPlanet.ixGetEmpire()
                        )
                    )

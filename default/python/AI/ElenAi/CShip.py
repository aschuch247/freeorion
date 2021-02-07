"""
This is a representation of a ship.
"""

from __future__ import print_function


class CShip(object):


    def __init__(self, ixShip, sSpecies, sHull, sPartList):
        self.__m_ixShip = ixShip
        self.__m_sSpecies = sSpecies
        self.__m_sHull = sHull

        # The same parts can be added multiple times to a ship design.

        self.__m_sPartList = sPartList

        self.__m_oFleet = None


    def ixGetShip(self):
        return self.__m_ixShip


    def sGetSpecies(self):
        return self.__m_sSpecies


    def sGetHull(self):
            return self.__m_sHull


    def bHasPart(self, sPart):
        return sPart in self.__m_sPartList


    def sGetPartList(self):
        return self.__m_sPartList


    def vSetFleet(self, oFleet):
        self.__m_oFleet = oFleet


    def oGetFleet(self):
        return self.__m_oFleet


    def vDump(self):
        print(
            'Ship %d with hull \'%s\' and parts %s is operated by species \'%s\'.' % (
                self.ixGetShip(),
                self.sGetHull(),
                self.sGetPartList(),
                self.sGetSpecies()
            )
        )

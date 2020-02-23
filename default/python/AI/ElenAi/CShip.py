"""
This is a representation of a ship.
"""

from __future__ import print_function


class CShip(object):


    def __init__(self, ixShip, sSpecies, sPartFrozenset):
        self.__m_ixShip = ixShip
        self.__m_sSpecies = sSpecies
        self.__m_sPartFrozenset = sPartFrozenset

        self.__m_oFleet = None


    def ixGetShip(self):
        return self.__m_ixShip


    def sGetSpecies(self):
        return self.__m_sSpecies


    def bHasPart(self, sPart):
        return sPart in self.__m_sPartFrozenset


    def sGetPartFrozenset(self):
        return self.__m_sPartFrozenset


    def vSetFleet(self, oFleet):
        self.__m_oFleet = oFleet


    def oGetFleet(self):
        return self.__m_oFleet


    def vDump(self):
        print(
            'Ship %d with parts %s is operated by species \'%s\'.' % (
                self.ixGetShip(),
                self.sGetPartFrozenset(),
                self.sGetSpecies()
            )
        )

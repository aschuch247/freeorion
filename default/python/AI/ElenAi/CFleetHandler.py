"""
The fleet handler has all known fleets registered.
"""

from __future__ import print_function


class CFleetHandler(object):


    def __init__(self):
        self.__m_dictFleet = dict()


    def vAddFleet(self, oFleet):
        self.__m_dictFleet[oFleet.ixGetFleet()] = oFleet


    def oGetFleet(self, ixFleet):
        return self.__m_dictFleet[ixFleet]


    def toGetFleet(self):
        for ixFleet, oFleet in self.__m_dictFleet.items():
            yield oFleet


    def vDump(self):
        print('--- fleet ---')

        for oFleet in self.toGetFleet():
            oFleet.vDump()

"""
This is a factory to convert a FreeOrion ship representation to an abstract representation.
"""

from ElenAi.CShip import CShip


class CShipConverter(object):


    def __init__(self, oFoShip):
        self.__m_oFoShip = oFoShip


    def __tsGetPart(self):
        for sPart in self.__m_oFoShip.design.parts:
            if (sPart != ''):
                yield sPart


    def oGetShip(self):
        return CShip(
            self.__m_oFoShip.id,
            self.__m_oFoShip.speciesName,
            frozenset(self.__tsGetPart())
        )

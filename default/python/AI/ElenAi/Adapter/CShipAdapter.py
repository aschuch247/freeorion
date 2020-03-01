"""
This is an adapter to convert a FreeOrion ship representation to an independent representation.
"""

from ElenAi.CShip import CShip


class CShipAdapter(object):


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
